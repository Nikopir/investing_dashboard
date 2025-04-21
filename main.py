from apscheduler.triggers.interval import IntervalTrigger

from dashboard import scheduler

if __name__ == '__main__':
    from dashboard.routes import *
    from dashboard.services import *

    with app.app_context():
        db.create_all()

    scheduler.add_job(func=update_all_shares_price, trigger=IntervalTrigger(minutes=5), id='prices')
    scheduler.add_job(func=load_shares_data, trigger=IntervalTrigger(minutes=5), id='datas')

    app.run(debug=True)
