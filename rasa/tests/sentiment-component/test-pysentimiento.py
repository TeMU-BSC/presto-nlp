from pysentimiento import SentimentAnalyzer
analyzer = SentimentAnalyzer(lang="es")
res = analyzer.predict("Estoy muy triste")
print(res)

