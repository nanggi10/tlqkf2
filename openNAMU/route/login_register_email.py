from route.tool.func import *
from flask import redirect, render_template, request, session, escape

def login_register_email_2():
    with get_db_connect() as conn:
        curs = conn.cursor()

        if not 'reg_id' in session:
            return redirect('/register')

        if request.method == 'POST':
            session['reg_key'] = load_random_key(32)

            user_email = re.sub(r'\\', '', request.form.get('email', ''))

            # 이메일 유효성 검사 추가
            if not is_valid_email(user_email):
                return easy_minify(conn, render_template(skin_check(conn),
                    imp = [get_lang(conn, 'member'), wiki_set(conn), wiki_custom(conn), wiki_css([0, 0])],
                    data = '''
                        <a href="/filter/email_filter">(''' + get_lang(conn, 'email_filter_list') + ''')</a>
                        <hr class="main_hr">
                        <p>@bl-m.kr ''' + get_lang(conn, 'email_only') + '''</p>
                        <form method="post">
                            <input placeholder="''' + get_lang(conn, 'email') + '''" name="email" type="text">
                            <hr class="main_hr">
                            <button type="submit">''' + get_lang(conn, 'save') + '''</button>
                        </form>
                    ''',
                    menu = [['user', get_lang(conn, 'return')]]
                ))
                
            email_data = re.search(r'@([^@]+)$', user_email)
            if email_data:
                email_data = email_data.group(1)

                curs.execute(db_change(
                    "select html from html_filter where html = ? and kind = 'email'"
                ), [email_data])
                if not curs.fetchall():                
                    return redirect('/filter/email_filter')

            curs.execute(db_change('select data from other where name = "email_title"'))
            sql_d = curs.fetchall()
            if sql_d and sql_d[0][0] != '':
                t_text = escape(sql_d[0][0])
            else:
                t_text = wiki_set(conn)[0] + ' key'

            curs.execute(db_change('select data from other where name = "email_text"'))
            sql_d = curs.fetchall()
            if sql_d and sql_d[0][0] != '':
                i_text = escape(sql_d[0][0]) + '\n\nKey : ' + str(session.get('reg_key'))
            else:
                i_text = 'Key : ' + str(session.get('reg_key'))


            curs.execute(db_change('select id from user_set where name = "email" and data = ?'), [user_email])
            if curs.fetchall():
                return re_error(conn, 35)

            if send_email(conn, user_email, t_text, i_text) == 0:
                return re_error(conn, 18)

            session['reg_email'] = user_email

            return redirect('/register/email/check')
        else:
            curs.execute(db_change('select data from other where name = "email_insert_text"'))
            sql_d = curs.fetchall()
            b_text = (sql_d[0][0] + '<hr class="main_hr">') if sql_d and sql_d[0][0] != '' else ''

            return easy_minify(conn, render_template(skin_check(conn),
                imp = [get_lang(conn, 'email'), wiki_set(conn), wiki_custom(conn), wiki_css([0, 0])],
                data = '''
                    <a href="/filter/email_filter">(''' + get_lang(conn, 'email_filter_list') + ''')</a>
                    <hr class="main_hr">
                    ''' + b_text + '''
                    <form method="post">
                        <input placeholder="''' + get_lang(conn, 'email') + '''" name="email" type="text">
                        <hr class="main_hr">
                        <button type="submit">''' + get_lang(conn, 'save') + '''</button>
                    </form>
                ''',
                menu = [['user', get_lang(conn, 'return')]]
            ))
