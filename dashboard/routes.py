from flask import render_template, redirect, url_for, flash, request
from flask_login import logout_user, login_required, login_user, current_user

from .forms import LoginForm, RegisterForm, ShareForm
from .models import User, Share
from dashboard import app, db, services


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        new_user = User(email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        flash('Вы успешно зарегистрированы!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы!', 'info')
    return redirect(url_for('login'))


@app.route('/')
def index():
    shares_pagination = Share.query.order_by(Share.name).paginate(error_out=False)
    return render_template(
        'dashboard/list.html',
        share_list=shares_pagination.items,
        page_obj=shares_pagination,
        user=current_user
    )


@app.route('/<int:share_id>')
def detail(share_id):
    share = Share.query.get_or_404(share_id)
    plot_div = services.get_graph(share)

    return render_template('dashboard/detail.html', share=share, plot_div=plot_div)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ShareForm()
    if form.validate_on_submit():
        new_share = Share(
            figi=form.figi.data,
            isin=form.isin.data,
            name=form.name.data,
            ticker=form.ticker.data,
            currency=form.currency.data,
            uid=form.uid.data
        )

        db.session.add(new_share)
        db.session.commit()
        flash(f'Инструмент "{new_share.name}" успешно добавлен!', 'success')
        return redirect(url_for('index'))

    return render_template('dashboard/create.html', form=form)


@app.route('/update/<int:share_id>', methods=['GET', 'POST'])
@login_required
def update(share_id: int):
    share = Share.query.get_or_404(share_id)
    form = ShareForm(obj=share, original_share=share)

    if form.validate_on_submit():
        form.populate_obj(share)
        db.session.commit()
        flash(f'Инструмент "{share.name}" успешно обновлен!', 'success')
        return redirect(url_for('index'))

    return render_template('dashboard/create.html', form=form, share=share)


@app.route('/delete/<int:share_id>', methods=['GET', 'POST'])
@login_required
def delete(share_id: int):
    share = Share.query.get_or_404(share_id)

    if request.method == 'POST':
        db.session.delete(share)
        db.session.commit()
        flash(f'Инструмент "{share.name}" успешно удален!', 'success')
        return redirect(url_for('index'))

    return render_template('dashboard/delete.html', share=share)
