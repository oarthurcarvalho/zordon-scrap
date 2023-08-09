import sys
from time import sleep

from GetterData import GetterData
from HandleDash import HandleDash


class AncineScraper:

    def __init__(self, url) -> None:
        self.dash = HandleDash(url)
        self.driver = self.dash.get_driver()
        self.nacionalidade = ['ESTRANGEIRA', 'BRASILEIRA']

    def get_week_option(self):

        while True:

            print(
                '''
                Digite a opção que você deseja fazer o scrap:
                => 'Nacional' - Obter os dados nacionais
                => 'Regional' - Obter os dados por estado e região
                => 'Sair'     - Sair do programa
                ''',
                end='\n\n'
            )

            option = input('Digite a opção: ').lower()

            if option not in ['nacional', 'regional', 'sair']:
                print(
                    'Você digitou um opção inexistente. Tente novamente',
                    end='\n\n'
                )
                continue

            return option

    def get_week_number(self):

        while True:
            print(
                "Digite o número da semana que deseja iniciar ou digite '0' para sair", end='\n\n')
            week_number_option = input("Digite a opção: ")

            try:
                int(week_number_option)
            except ValueError:
                print('Você não digitou um número inteiro. Tente novamente!')
                continue

            if week_number_option == 0:
                self.driver.quit()
                sys.exit()

            return week_number_option

    def scrap(self, by, num_week):
        self.dash.clear_filters()


if __name__ == '__main__':
    url = 'https://app.powerbi.com/view?r=eyJrIjoiM2ViZGRmMjctYjZlNC00NjI4LWFiZDEtMDAzZjk2OTU2OGYyIiwidCI6ImIwYThiNWFkLTU5MGQtNGZiYS1hZmY4LWUzMDc0YWI0MzVhNyJ9&pageName=ReportSectiona448b45fb6e3695eb8ba'
    ancine = AncineScraper(url)
    week_number = ancine.get_week_number()
    option = ancine.get_week_option()
    ancine.scrap(option, week_number)
