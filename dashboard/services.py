from datetime import timedelta

from plotly.graph_objs import Scatter
from plotly.offline import plot
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now

from .models import Share
from dashboard import app, db


def get_graph(share):
    tinkoff_token = app.config.get('TINKOFF_TOKEN')
    if not tinkoff_token:
        return '<p>Ошибка: Не настроен токен Tinkoff API.</p>'

    try:
        with Client(tinkoff_token) as client:
            x_data, y_data = [], []
            for candle in client.get_all_candles(
                    figi=share.figi,
                    from_=now() - timedelta(days=90),
                    interval=CandleInterval.CANDLE_INTERVAL_DAY,
            ):
                x_data.append(candle.time.date())
                y_data.append(candle.close.units + candle.close.nano * 1e-9)

        if not x_data:
            return '<p>Нет данных для построения графика за выбранный период.</p>'

        plot_div = plot(
            [
                Scatter(
                    x=x_data,
                    y=y_data,
                    mode='lines',
                    name=f'{share.ticker} Price',
                    opacity=0.8,
                    marker_color='blue',
                )
            ],
            output_type='div',
            show_link=False,
            link_text=''
        )

        return plot_div
    except Exception as e:
        return f'<p>Ошибка загрузки данных графика: {e}</p>'


def get_last_data(share):
    tinkoff_token = app.config.get('TINKOFF_TOKEN')
    if not tinkoff_token:
        return [None, None]

    try:
        with Client(tinkoff_token) as client:
            resp = client.market_data.get_last_prices(figi=[share.figi])
            if not resp.last_prices:
                return [None, None]

            resp = resp.last_prices.pop()
            price = int((resp.price.units + resp.price.nano * 1e-9) * 1_000_000) / 1_000_000
            return [price, resp.time]
    except Exception:
        return [None, None]


def update_all_shares_price():
    with app.app_context():
        shares = Share.query.all()
        updated_count = 0

        for share in shares:
            [last_price, updated_at] = get_last_data(share)
            if last_price is not None:
                is_trend_high = None
                if share.last_price is not None:
                    if last_price > share.last_price:
                        is_trend_high = True
                    elif last_price < share.last_price:
                        is_trend_high = False

                share.last_price = last_price
                share.is_trend_high = is_trend_high
                share.updated_at = updated_at
                updated_count += 1

                db.session.add(share)
                db.session.commit()

                print(f'Updated price of {share.ticker}: {share.last_price} {share.currency}.')

        print(f'Finished price update. {updated_count} shares updated.')


def load_shares_data():
    tinkoff_token = app.config.get('TINKOFF_TOKEN')
    if not tinkoff_token:
        return

    added_count = 0
    existing_count = 0

    with app.app_context():
        with Client(tinkoff_token) as client:
            shares_response = client.instruments.shares()
            print(f"Fetched {len(shares_response.instruments)} potential shares from Tinkoff API.")

            for share_data in shares_response.instruments:
                existing_share = Share.query.filter_by(uid=share_data.uid).first()
                if existing_share:
                    existing_count += 1
                    continue

                new_share = Share(
                    figi=share_data.figi,
                    name=share_data.name,
                    isin=share_data.isin,
                    ticker=share_data.ticker,
                    currency=share_data.currency,
                    uid=share_data.uid
                )

                db.session.add(new_share)
                added_count += 1

            db.session.commit()
            print(f"Finished loading shares. Added {added_count} new shares, {existing_count} already existed.")
