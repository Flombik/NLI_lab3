import nltk
from nltk.treeprettyprinter import TreePrettyPrinter
import docx
from flask import Flask
from flask import render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, TextAreaField
from werkzeug.utils import secure_filename

grammar = """
       P: {<IN>}
       PV: {<V.*|MD>}
       MM: {<DT|PR.*|JJ|NN.*>+}    
       PP: {<IN><MM>}               
       PV: {<V.*><MM|RB|PP|LINK>+$} 
       LINK: {<MM><PV>}           
       """
cp = nltk.RegexpParser(grammar)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a really really really really long secret key'


class AnalysisForm(FlaskForm):
    text = TextAreaField("Текст: ")
    file = FileField('Анализ файла')
    submit = SubmitField("Анализ")


@app.route('/analysis/', methods=['get', 'post'])
def analysis():
    form = AnalysisForm()
    if form.validate_on_submit():
        if form.text.data:
            text = form.text.data
        if form.file.data:
            filename = secure_filename(form.file.data.filename)
            form.file.data.save('uploads/' + filename)
            doc = docx.Document('uploads/' + filename)
            text = ''
            for paragraph in doc.paragraphs:
                text = ' '.join([text, paragraph.text])
        text = text.replace('\n', '')
        sentences = text.split('.')
        results = []
        for sentence in sentences:
            if sentence == '':
                continue
            tokens = nltk.word_tokenize(sentence)
            tokens = nltk.pos_tag(tokens)
            processed_tokens = []
            for token in tokens:
                if token[1] != ',' and token[1] != '.':
                    processed_tokens.append(token)
            result = cp.parse(processed_tokens)
            results.append(TreePrettyPrinter(result).text())
        return render_template('show_result.html', results=results)
    return render_template('analysis.html', form=form)


@app.route('/help/')
def help():
    return render_template('help.html')


@app.route('/')
def index():
    return redirect(url_for('help'))


if __name__ == '__main__':
    app.run()
