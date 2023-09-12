import subprocess

# Lista com o nome de cada spider
spiders = ['amz', 'fp', 'ct', 'imdb', 'gp', 'tt', 'gp']

for spider in spiders:
    comando = f'scrapy crawl {spider}'
    subprocess.run(comando, shell=True)
