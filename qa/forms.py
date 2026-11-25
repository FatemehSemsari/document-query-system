from django import forms


class AskQuestionForm(forms.Form):

    question = forms.CharField(
        label='Question',
        max_length=1000,
        widget=forms.Textarea(
            attrs={
                'rows': 5,
                'cols': 70,
                'dir': 'auto'
            }
        )
    )