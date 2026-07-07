from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# データベースの設定（todo.dbというファイルが自動作成されます）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# データベースの設計図（モデル）
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    # ※完了フラグや期限などのカラムは、今後のステップで追加します

# アプリ起動時にデータベースを作成
with app.app_context():
    db.create_all()

# 一覧表示機能（トップページ）
@app.route('/')
def index():
    # データベースからすべてのタスクを取得
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

# タスク登録機能
@app.route('/add', methods=['POST'])
def add():
    # フォームから入力されたタスク名を取得
    title = request.form.get('title')
    if title:
        # 新しいタスクを作成してデータベースに保存
        new_task = Task(title=title)
        db.session.add(new_task)
        db.session.commit()
    # トップページにリダイレクト
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 開発モードでアプリを起動
    app.run(debug=True)