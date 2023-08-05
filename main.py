from SETTINGS import *

@app.route("/")
def home():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
    posts = []
    if 'order_by' in request.args:
        posts = PostFilterTags(int(request.args['order_by']))
    else:
        d = dataManager()
        posts = d.getAll('post')
    break_line = 1
    p = []
    line = []
    for x in range(len(posts)):
        po = [posts[x][0],eval(posts[x][1])]
        if break_line < 4: # Not is a line full
            line.append(po)
        if len(posts)-x < 4: # Not have to complete a line
            break_line = 3 # break a line
        if break_line == 3: # Break a line
            p.append(line)
            line = []
            break_line = 1
        break_line += 1
    posts = p
    return render_template("home.html", current_user=current_user,database=dataManager(),posts = posts)

@app.route('/p/<postId>')
def post(postId):
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
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
                flash('A postagem não existe.','error')
                return redirect('/')
        else:
            flash('Para deletar uma postagem precisa-se de um Id','error')
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
                "autorId":0
            }
            if len(title) > 3 and len(title) < 255:
                if len(content) > 7 and len(content) < 30000:
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
                    flash('O Conteúdo da sua postagem deve ter no minímo 7 caracteres e no máximo 30000 caracteres.','warning')
            else:
                flash('O Título da sua postagem deve ter no minímo 3 caracteres e no máximo 255 caracteres.','warning')
        return render_template('create.html',current_user=current_user,database=dataManager())
    else:
        flash('Precisa estar logado.','error')
        return redirect('/')
    
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
                if not tagName in ['','None',None]:
                    tags = []
                    for tag in d.getAll('tags'):
                        tags.append(tag[1].lower())
                    if not tagName in tags:
                        d.insert('tags',DB_TAGS_TABLE_COLUMNS[1:],[str(tagName),])
                        flash('Tag criada!','info')
                    else:
                        flash('Está tag ja existe.','warning')
                else:
                    flash('A tag precisa ter um nome.','warning')
            if 'tag-d' in request.form:
                tagId = request.form.get('tags')
                if d.get('tags',int(tagId)):
                    d.delete('tags',int(tagId))
                    flash('Tag apagada','info')
                else:
                    flash('Esta tag não existe!','warning')
        return render_template('admin.html',current_user=current_user,database=dataManager())
    else:
        flash('Você tem que estar logado e ser administrador','warning')
        return redirect('/')

@app.route("/oauth/callback")
def callback():
    current_user = User(request.args["code"])
    session["token"] = current_user.access_token
    d = dataManager()
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
    return redirect("/")

@app.route("/logout")
def logout():
    if "token" in session:
        session.clear()
        return redirect("/")

@app.route("/u")
def user():
    userId = request.args["id"]
    d = dataManager()

    u = User(id=userId)
    u.getMeInDatabase()
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
        if str(userId) == str(current_user.id):
            flash('Você está visualizando seu perfil.','info')

    return render_template("user.html", current_user=current_user, user=u)

@app.route("/config", methods=["POST", "get"])
def config():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
    if current_user and request.method == "POST":
        color = request.form.get("highlight")  # Highlight color
        about = request.form.get("about")  # About
        urls = request.form.get('url_index') # get urls
        urlsDict = {}
        if int(urls) >= 1:
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
        current_user.aboutme = about
        current_user.links = urlsDict
        
        d.update('users',DB_USERS_TABLE_COLUMNS[1:],(str(current_user.__dict__),),current_user.id) # update in database
    return render_template("config.html", current_user=current_user)

# Files Returners
@app.route("/about.html")
def about():
    f = open(app.template_folder + "/loadable/about.html", "rb").read()
    return f

@app.route('/richtexteditor.html')
def rct():
    f = open(app.template_folder + "/loadable/richtexteditor.html", "rb").read()
    return f

if __name__ == "__main__":
    print("""
    \n\n
    Server Open
    - http://localhost:5000
    \n\n
    """)
    app.run(debug=True)