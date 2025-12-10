from django.core.management.base import BaseCommand
from santa_game.models import Participant


class Command(BaseCommand):
    help = 'Добавить участников Secret Santa в базу данных'

    def handle(self, *args, **options):
        participants_data = [
            ("Abdikadirov Muxammedali Marqabay uli", "998888559444"),
            ("Abdujabborov Rasul", "998977712425"),
            ("Abdullayev Muxammadqodir Ma'ruf o'g'li", "998888559444"),
            ("Abdusattarov Umidjon", "998911320204"),
            ("Ahadova Ruxshona Ravshan qizi", "998339896004"),
            ("Ahmadov Sardor Sherzod o'g'li", "998948201777"),
            ("Babaniyazov Xakimboy Rustam o'g'li", "998935778199"),
            ("Begmatov Jahongir", "998931809080"),
            ("Bekchanova Laylo Ilxambayevna", "998971575910"),
            ("Bogdanova Laylo Aziz qizi", "998901755351"),
            ("Juraxonova Shohista Jasurxon qizi", "998990447538"),
            ("Karimov Sardorbek Halimjon o'g'li", "998913657941"),
            ("Kuchkarova Rushaniya Baxtiyorovna", "998976871883"),
            ("Mamajonov Elyorjon Erkinjon o'g'li", "998911643638"),
            ("Mansurov Abdusamad Rustamjon o'g'li", "998977515747"),
            ("Miraximova Maftuna Tolibjon qizi", "998935284664"),
            ("Miryunusov Mirsaid Umidjon o'g'li", "998900103221"),
            ("Mirzayev Javohir Jahongir o'g'li", "998980770604"),
            ("Obidov Ibrohim Mirjalol O'g'li", "998909008111"),
            ("Olimjonov Mirzabek Olimjonovich", "998956369555"),
            ("Qodirova Charos", "998502075949"),
            ("Qaxramonov Fayzullox Shuxratbek o'g'li", "998996093110"),
            ("Rabbimova Mushtariy Azizbek qizi", "998958422522"),
            ("Sardaliyeva Asmar Ansar qizi", "998992700804"),
            ("Shaxobiddinov Xadiyatulloh", "998995488015"),
            ("Sodiqov Amirxon Azizxon o'g'li", "998903376144"),
            ("Sodiqov Boburxon Azizxon o'g'li", "998935338727"),
            ("Spivak Margarita Vitalevna", "998900277990"),
            ("Tangmatov Begzod Olimjonovich", "998909470503"),
            ("Tashpulatov To'xtamurod Shuxratovich", "998885993533"),
            ("Xo'dayberdiyev Jamshidbek Murodovich", "998909892387"),
            ("Xojiyev Kamoliddin", "998901979595"),
            ("Xolmuratova Mashxura Yo'ldashovna", "998773131300"),
            ("Ziyodov Asadbek Asqar o'g'li", "998946749357"),
            ("Abdullayev Azizbek Shavkat O'g'li", "998976081211"),
            ("Ashurov Oybek Shavkatovich", "998908680002"),
            ("Axmadova Madina Lazizovna", "998908999800"),
            ("Bozorova Gulimoh Ortiq qizi", "998909466515"),
            ("Diyorov Jahongir Muxtor o'g'li", "998908715545"),
            ("Komilov Sunnat Rustamovich", "998200008011"),
            ("Narziyev Toxirbek Akramovich", "998973161552"),
            ("Na'matov Jaxongir Erkin o'g'li", "998914680101"),
            ("Qazoqov Dilshod Sherzod o'g'li", "998914560111"),
            ("Qazoqov Quvonchbek Xayrullo o'g'li", "998972222941"),
            ("Sadikova Sabina Furkatovna", "998878272100"),
            ("To'rayev Muhammadjon Mehroj o'g'li", "998908950202"),
            ("Zoirova Marjona Shuhrat qizi", "998908931515"),
            ("Doniyorov Miraziz To'ra o'g'li", "998976739991"),
            ("Sobirov Asilbek Sherzod o'g'li", "998904644303"),
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for name, phone in participants_data:
            # Очищаем номер телефона от пробелов и добавляем код страны если нужно
            phone_clean = phone.replace(" ", "").replace("+", "")
            
            # Проверяем, существует ли участник с таким номером
            participant, created = Participant.objects.get_or_create(
                phone_number=phone_clean,
                defaults={
                    'name': name,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Добавлен: {name} ({phone_clean})')
                )
            else:
                # Если участник уже существует, обновляем имя
                if participant.name != name:
                    participant.name = name
                    participant.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Обновлён: {name} ({phone_clean})')
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'- Пропущен (уже существует): {name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n'
                f'Готово!\n'
                f'Добавлено: {created_count}\n'
                f'Обновлено: {updated_count}\n'
                f'Пропущено: {skipped_count}\n'
                f'Всего участников: {Participant.objects.count()}'
            )
        )
