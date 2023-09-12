from SETTINGS import *
from discord import SyncWebhook, Embed

@app.route("/")
def home():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
    print(current_user)
    posts = []
    if 'order_by' in request.args:
        posts = PostFilter(int(request.args['order_by']))
    else:
        posts = dataManager().getAll('post')
    break_line = 1
    p = []
    line = []
    for x in range(len(posts)):
        po = [posts[x][0],posts[x][1]]
        if break_line < 4: # Not is a line full
            line.append(po)
        if len(posts)-x < 3: # Not have to complete a line
            break_line = 3 # break a line
        if break_line >= 3: # Break a line
            p.append(line)
            line = []
            break_line = 1
        break_line += 1
    posts = p
    return render_template("home.html", current_user=current_user,database=dataManager(),posts = posts)

@app.route('/p/<postId>',methods=["post",'get'])
def post(postId):
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
        if request.method == "POST":
            d = dataManager()
            post = eval(d.get('post',postId)[1])
            if "-" in request.form:
                if current_user.id in post['whounlike']: # Remove Unlike
                    post['whounlike'].pop(post['whounlike'].index(current_user.id))
                    d.update('post',['data',],[str(post),],postId)
                elif current_user.id in post['wholike']: # Remove from like and add for unlike
                    post['wholike'].pop(post['wholike'].index(current_user.id))
                    post['whounlike'].append(current_user.id)
                    d.update('post',['data',],[str(post),],postId)
                else:
                    post['whounlike'].append(current_user.id)
                    d.update('post',['data',],[str(post),],postId)
            elif "+" in request.form:
                if current_user.id in post['wholike']: # Remove like
                    post['wholike'].pop(post['wholike'].index(current_user.id))
                    d.update('post',['data',],[str(post),],postId)
                elif current_user.id in post['whounlike']: # Remove from unlike and add for like
                    post['whounlike'].pop(post['whounlike'].index(current_user.id))
                    post['wholike'].append(current_user.id)
                    d.update('post',['data',],[str(post),],postId)
                else:
                    post['wholike'].append(current_user.id)
                    d.update('post',['data',],[str(post),],postId)

    return render_template('post.html',current_user=current_user,database = dataManager(),postId=postId)

@app.route('/d',methods=['get','post'])
def deletePost():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
        if "pId" in request.args:
            d = dataManager()
            post = d.get('post',int(request.args['pId']))
            if post:
                if "POST" == request.method:
                    d.delete('post',post[0])
                    return redirect('/')
                return render_template('delete_post.html',current_user=current_user,postT=post)
            else:
                flash('A postagem não existe.','danger')
                return redirect('/')
        else:
            flash('Para deletar uma postagem precisa-se de um Id','danger')
            return redirect('/')
    else:
        flash('Você precisa estar logado para fazer esta ação','warning')
        return redirect('/')

@app.route('/create',methods=['POST','GET'])
def create():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
    if current_user:
        if request.method == 'POST':
            d = dataManager()
            tags = eval(request.form.get('tags-s'))
            title = str(request.form.get('post-title'))
            content = str(request.form.get('rte-content'))
            post = {
                "title":"",
                "tags":[],
                "content":"",
                "date":"",
                "autorId":0,
                "wholike":[],
                "whounlike":[]
            }
            if len(title) > 3 and len(title) < 255:
                if len(content) > 7 and len(content) < 17500:
                    post['title'] = title
                    post['content'] = content
                    if len(str(tags)) == 1:
                        tags = [tags,]
                    if len(tags) == 1:
                        tags = [tags[0],]
                    post['tags'] = tags
                    post['date'] = datetime.now().strftime(DB_DATETIME_STR)
                    post['autorId'] = int(current_user.id)
                    d.insert('post',DB_POST_TABLE_COLUMNS[1:],[str(post)])
                    flash('Postagem criada!')
                    return redirect('/')
                else:
                    flash('O Conteúdo da sua postagem deve ter no minímo 7 caracteres e no máximo 17500 caracteres.','warning')
            else:
                flash('O Título da sua postagem deve ter no minímo 3 caracteres e no máximo 255 caracteres.','warning')
        return render_template('create.html',current_user=current_user,database=dataManager())
    else:
        flash('Precisa estar logado.','danger')
        return redirect('/')

@app.route('/edit',methods=["POST","GET"])
def edit():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
    if 'pId' in request.args:
        post = eval(dataManager().get('post',request.args['pId'])[1])
        if current_user and current_user.id == post['autorId']:
            return render_template('edit.html',current_user=current_user,post=post,database=dataManager())
    else:
        return redirect('/err?err=No%20Post%20Id')

@app.route('/admin',methods=['POST','GET'])
def admin():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
    if current_user and current_user.admin:
        d = dataManager()
        if request.method == 'POST':
            if 'tag-c' in request.form:
                tagName = request.form.get('tag-c-name')
                allTagsName = []
                if (not tagName in ['','None',None]):
                    tags = []
                    for tag in d.getAll('tags'):
                        tags.append(tag[1].lower())
                    if not tagName.lower() in tags:
                        d.insert('tags',DB_TAGS_TABLE_COLUMNS[1:],[str(tagName),])
                        flash('Tag criada!','info')
                    else:
                        flash('Está tag ja existe.','warning')
                else:
                    flash('A tag precisa ter um nome.','warning')
            elif 'tag-d' in request.form:
                tagId = request.form.get('tags')
                if d.get('tags',int(tagId)):
                    d.delete('tags',int(tagId))
                    flash('Tag apagada','info')
                else:
                    flash('Esta tag não existe!','warning')
            elif 'sug-d' in request.form:
                flash('Está sugestão foi deletada.','info')
                suggest = eval(request.form.get('sug-d'))
                sender = User(id=suggest['authorId'])
                sender.notifications.append({'id':len(sender.notifications)+1,'date':datetime.now().strftime(DB_DATETIME_STR),'message':"Sua sugestão foi rejeitada.",'type':'danger'})
                d.update('users',["data"],[str(sender.__dict__)],sender.id)
                if sender.recv_emails_noti:
                    msg = Message(subject='Nova Notificação!',recipients=[sender.user['email']])
                    msg.body = f"Você recebeu uma nova notificação! Verifique-a aqui: {SITE_URL}"
                    mail.send(msg)
            elif 'new-c' in request.form:
                newData = {
                    'authorId':current_user.id,
                    'content':'',
                    'date':datetime.now().strftime(DB_DATETIME_STR)
                }
                newData['content']=request.form.get('new-cont')
                d.insert('news',DB_NEWS_TABLE_COLUMN[1:],[str(newData)])
                emb = Embed(
                    title="Nova Notícia!",
                    description=f"Nova notícia! caso queira ver, clique [aqui]({SITE_URL}/news)",
                    color=0x0F23EC,
                    timestamp=datetime.now()
                )
                emb.set_author(name=current_user.user['username'],icon_url=current_user.user['avatar_url'])
                webhook = SyncWebhook.from_url(WEBHOOK_SUGGESTIONS)
                webhook.send(embed=emb)
                users = dataManager().getAll('users')
                for user in users:
                    u = User(id=user[0])
                    if u.recv_emails_noti:
                        msg = Message(subject='Nova Notícia!',recipients=[u.user['email']])
                        msg.body = f"Uma nova notícia saiu! verifique aqui: {SITE_URL}/news"
                        mail.send(msg)
                flash('Notícia criada!','info')
            elif 'user-sadm' in request.form:
                userId = request.form.get('users')
                user = eval(d.get('users',userId)[1])
                if not user['admin']:
                    user['admin'] = True
                    user['notifications'].append({'id':len(user['notifications'])+1,'date':datetime.now().strftime(DB_DATETIME_STR),'message':"Você se tornou Administrador.",'type':'success'})
                    if user.recv_emails_noti:
                        msg = Message(subject='Nova Notificação!',recipients=[user.user['email']])
                        msg.body = f"Você recebeu uma nova notificação! Verifique-a aqui: {SITE_URL}"
                        mail.send(msg)
                    d.update('users',DB_USERS_TABLE_COLUMNS[1:],[str(user)],userId)
                    flash('Usuario agora é administrador','info')
                else:
                    flash('Este usuario ja era administrador','danger')
            else:
                pass
        else:
            pass
        return render_template('admin.html',current_user=current_user,database=dataManager())
    else:
        flash('Você tem que estar logado e ser administrador','warning')
        return redirect('/')

@app.route('/news',methods=['post','get'])
def news():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
        if current_user.admin:
            if request.method == "POST":
                if 'delete' in request.form:
                    dataManager().delete('news',request.form.get('delete'))
    return render_template('news.html',current_user=current_user, database=dataManager())

@app.route("/oauth/callback")
def callback():
    d = dataManager()
    try:
        current_user = User(request.args["code"])
    except Exception as err:
        print(err)
        return redirect(f'/err?err={err}')
    
    session["token"] = current_user.access_token
    if d.get("users", current_user.user["id"]):
        # Update
        d.update(
            "users", ["data"], [str(current_user.__dict__)], current_user.user["id"]
        )  # Update User
    else:
        d.is_registered(
            "users",
            current_user.user["id"],
            True,
            (
                DB_USERS_TABLE_COLUMNS,
                [current_user.user["id"], str(current_user.__dict__)],
            ),
        )
    if current_user:
        msg = Message(subject='Olá!',recipients=[current_user.user['email']])
        msg.body = "Você fez login em sua conta hoje? se não recomendamos fortemente que altere sua senha no Discord. Caso tenha sido você, Seja bem-vindo(a)!"
        mail.send(msg)
    return redirect("/")

@app.route("/logout")
def logout():
    if "token" in session:
        session.clear()
        return redirect("/")
    else:
        return redirect("/")

@app.route("/u",methods=["post",'get'])
def user():
    userId = request.args["id"]
    d = dataManager()

    u = User(id=userId)
    u.getMeInDatabase()
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
        if 'POST' == request.method:
            if "follow" in request.form:
                if not current_user.id in u.followers and not current_user.id == u.id:
                    u.followers.append(current_user.id)
                    current_user.folowing.append(u.id)
                    u.notifications.append({'id':len(u.notifications)+1,'date':datetime.now().strftime(DB_DATETIME_STR),'message':f"{current_user.user['username']} Começou a te seguir",'type':'success'})
                    if u.recv_emails_noti:
                        msg = Message(subject='Nova Notificação!',recipients=[u.user['email']])
                        msg.body = f"Você recebeu uma nova notificação! Verifique-a aqui: {SITE_URL}"
                        mail.send(msg)
                    dataManager().update('users',['data'],[str(u.__dict__)],u.id)
                    dataManager().update('users',['data'],[str(current_user.__dict__)],current_user.id)
            elif "unfollow" in request.form:
                if current_user.id in u.followers and not current_user.id == u.id:
                    u.followers.pop(u.followers.index(current_user.id))
                    current_user.folowing.pop(current_user.folowing.index(current_user.id))
                    u.notifications.append({'id':len(u.notifications)+1,'date':datetime.now().strftime(DB_DATETIME_STR),'message':f"{current_user.user['username']} Deixou de te seguir",'type':'danger'})
                    if u.recv_emails_noti:
                        msg = Message(subject='Nova Notificação!',recipients=[u.user['email']])
                        msg.body = f"Você recebeu uma nova notificação! Verifique-a aqui: {SITE_URL}"
                        mail.send(msg)
                    dataManager().update('users',['data'],[str(u.__dict__)],u.id)
                    dataManager().update('users',['data'],[str(current_user.__dict__)],current_user.id)

    return render_template("user.html", current_user=current_user, user=u,database=dataManager())

@app.route("/config", methods=["POST", "get"])
def config():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
    
    if current_user and request.method == "POST":
        color = request.form.get("highlight")  # Highlight color
        color2 = request.form.get('gcolor') # Gradient color 2
        about = request.form.get("about")  # About
        urls = request.form.get('url_index') # get urls
        news_email = request.form.get('news-email')
        #print(news_email)
        noti_email = request.form.get('noti-email')
        urlsDict = {}
        if type(urls) != int:
            if urls in ["0","",None," "]:
                urls = 0
            else:
                urls = int(urls)

        if urls >= 1:
            for url in range(int(urls)):
                x = {}
                x['title'] = request.form.get('url-title'+str(url))
                x['url'] = request.form.get('url-url'+str(url))
                x['type'] = request.form.get('url-type'+str(url))
                urlsDict[str(url)] = x

        if (about in ["",' ', None, "None"]) or len(about) < 3:
            about = "Olá!"

        d = dataManager()
        # Update user
        current_user.highlight_color = color
        current_user.gradient_color = color2
        current_user.aboutme = about
        current_user.links = urlsDict
        if news_email == 'on':
            news_email = True
        else:
            news_email = False
        if noti_email == 'on':
            noti_email = True
        else:
            noti_email = False
        current_user.recv_emails_news = noti_email
        current_user.recv_emails_noti = news_email

        d.update('users',DB_USERS_TABLE_COLUMNS[1:],(str(current_user.__dict__),),current_user.id) # update in database
    return render_template("config.html", current_user=current_user)

@app.route('/suggest',methods=["POST","GET"])
def suggest():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
        if current_user:
            if 'POST' == request.method:
                content = request.form.get('suggest')
                data  = {
                    'content':"",
                    'authorId':0,
                    'date':"",
                    'wholiked':[],
                    'whounliked':[]
                }
                data['content'] = content
                data['date'] = datetime.now().strftime(DB_DATETIME_STR)
                data['authorId'] = current_user.id
                dataManager().insert('suggestions',DB_SUGGESTIONS_TABLE_COLUMNS[1:],[str(data)])
                flash('Sua Sugestão foi enviado com sucesso','sucess')
                emb = Embed(
                    title="Nova Sugestão!",
                    description=data['content'],
                    color=0xECE40F,
                    timestamp=datetime.now()
                )
                emb.set_author(name=current_user.user['username'],icon_url=current_user.user['avatar_url'])
                webhook = SyncWebhook.from_url(WEBHOOK_SUGGESTIONS)
                webhook.send(embed=emb)
                return redirect('/')
            return render_template('sugest.html',current_user=current_user)

@app.route('/suggestions',methods=["POST","GET"])
def suggestions():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
        if request.method == "POST":
            d = dataManager()
            if '+' in request.form:
                sug = dataManager().get('suggestions',int(request.form.get('+')))
                data = eval(sug[1])
                if current_user.id in data['whounliked']:
                    data['whounliked'].pop(data['whounliked'].index(current_user.id))
                    data['wholiked'].append(current_user.id)
                    d.update('suggestions',['data',],[str(data),],sug[0])
                elif current_user.id in data['wholiked']:
                    data['wholiked'].pop(data['wholiked'].index(current_user.id))
                    d.update('suggestions',['data',],[str(data),],sug[0])
                else:
                    data['wholiked'].append(current_user.id)
                    d.update('suggestions',['data',],[str(data),],sug[0])
            elif '-' in request.form:
                sug = dataManager().get('suggestions',int(request.form.get('-')))
                data = eval(sug[1])
                if current_user.id in data['wholiked']:
                    data['wholiked'].pop(data['wholiked'].index(current_user.id))
                    data['whounliked'].append(current_user.id)
                    d.update('suggestions',['data',],[str(data),],sug[0])
                elif current_user.id in data['whounliked']:
                    data['whounliked'].pop(data['whounliked'].index(current_user.id))
                    d.update('suggestions',['data',],[str(data),],sug[0])
                else:
                    data['whounliked'].append(current_user.id)
                    d.update('suggestions',['data',],[str(data),],sug[0])


    return render_template('suggestions.html',current_user=current_user,database=dataManager())

@app.route('/encrypt',methods=["POST","GET"])
def encrypt():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
    if request.method == "POST":
        con = request.form.get('content')
        con = pye.encrypt(str(con))
        return render_template('encrypt.html',current_user=current_user,content=con)
    return render_template('encrypt.html',current_user=current_user,content="")
#others
@app.route('/err')
def error():
    if 'err' in request.args:
        flash(f'Um erro ocorreu: {request.args["err"]}','danger')
        return redirect('/')
    else:
        return redirect('/')

@app.errorhandler(404)
def page_not_found(error):
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
    return render_template('404.html',current_user=current_user,erro=error)

@app.route('/dlnall')
def deleteallnotify():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
        if current_user:
            current_user.notifications = []
            dataManager().update('users',['data'],[str(current_user.__dict__)],current_user.id)
            flash('Todas as notificações foram apagadas!','info')
            return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/dln')
def deletenotify():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
        if current_user:
            if 'id' in request.args:
                current_user.notifications.pop(int(request.args['id'])-1)
                dataManager().update('users',['data'],[str(current_user.__dict__)],current_user.id)
                return redirect('/')
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')

# Files Returners
@app.route("/about.html")
def about():
    f = open(app.template_folder + "/loadable/about.html", "rb").read()
    return f

@app.route('/richtexteditor.html')
def rct():
    f = open(app.template_folder + "/loadable/richtexteditor.html", "rb").read()
    return f

@app.route('/readme_viewer.html')
def rdmv():
    f =open(app.template_folder + "/loadable/readme_viewer.html", "rb").read()
    return f

@app.route('/readme.md')
def rdm():
    f = open('./readme.md','rb').read()
    return f

@app.route('/gnotify.html')
def notify():
    f = open('./pages/loadable/notify.html','rb').read()
    return f

@app.route('/flwrs.html')
def flwrs():
    f = open('./pages/loadable/followers.html','rb').read()
    return f


if __name__ == "__main__":
    print("""
    \n\n
    Server Open
    - http://localhost:5000
    \n\n
    """)
    dcemb = Embed(
        title="O Site Está ONLINE!",
        description="PGL: O site está online! <:9110zeropeace:1016329175218540604>",
        colour=0x32CE0A,
        timestamp=datetime.now()
    )
    webhook = SyncWebhook.from_url(WEBHOOK_SUGGESTIONS)
    webhook.send(embed=dcemb)
    app.run(debug=True)