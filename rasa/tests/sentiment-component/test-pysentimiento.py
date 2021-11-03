from pysentimiento import SentimentAnalyzer
analyzer = SentimentAnalyzer(lang="es")
res = analyzer.predict("Hola me siento mal")
res
