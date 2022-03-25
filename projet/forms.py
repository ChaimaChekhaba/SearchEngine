from django import forms


class IRForm(forms.Form):
    cleaning_choices = (
        ("0", "Without cleaning"),
        ("1", "Removing stop words"),
        ("2", "Stemming with Porter"),
        ("3", "Stemming with Krovetz"),
        ("4", "Lemmatization"),
        ("5", "English Analyser"),
        )
    cleaning = forms.ChoiceField(
        choices=cleaning_choices,
        required=True,
        widget=forms.RadioSelect,
    )
    similarity_choices = (
        ("0", "TFIDF Similarity"),
        ("1", "BM25 Similarity"),
    )
    similarity = forms.ChoiceField(
        choices=similarity_choices,
        required=True,
        widget=forms.RadioSelect,
    )
    improve_choices = (
        ("0", "None"),
        ("1", "WordNet"),
        ("2", "Word Embedding"),
    )
    improve = forms.ChoiceField(
        choices=improve_choices,
        required=True,
        widget=forms.RadioSelect,
    )
    query = forms.CharField(max_length=200, label='Search ...', required=True)




