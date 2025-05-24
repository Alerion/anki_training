import typer

from anki_training.irregular_verbs_command import irregular_verbs_command
from anki_training.sein_oder_haben_command import sein_oder_haben_command
from anki_training.translate_command import translate_command

app = typer.Typer()

# python -m main irregular_verbs
app.command("irregular_verbs")(irregular_verbs_command)
# python -m main sein_oder_haben
app.command("sein_oder_haben")(sein_oder_haben_command)
# python -m main translate
app.command("translate")(translate_command)


if __name__ == "__main__":
    app()
