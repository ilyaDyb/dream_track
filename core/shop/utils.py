stickers = [
    ("☀️ Early Bird", "Ты встал до будильника. Монстр дисциплины", "https://i.imgur.com/U8h0Fsl.png", "common", False),
    ("📅 Habit Builder", "Один день — это начало. Продолжай!", "https://i.imgur.com/xqU90qZ.png", "common", False),
    ("📵 Focus Master", "Никаких отвлечений. Ты в зоне", "https://i.imgur.com/9Rztrpw.png", "common", False),
    ("📖 10 Pages Rule", "Ты прочитал свои 10 страниц", "https://i.imgur.com/RZsmPYv.png", "common", False),
    ("✅ One Done", "Ты выполнил хотя бы одну задачу", "https://i.imgur.com/OyDxyge.png", "common", False),
    ("🚶 Walk & Think", "Ты прогулялся и дал мозгу отдохнуть", "https://i.imgur.com/dJZfzht.png", "common", False),
    
    ("🥗 Health Streak", "Ты поел здоровую еду. Красавчик", "https://i.imgur.com/3IpHFaF.png", "rare", False),
    ("📓 Journaled Today", "Ты записал свои мысли — душа благодарит", "https://i.imgur.com/SNRn9fS.png", "rare", False),
    ("🧼 Clean Desk", "Ты убрался на столе. Ментальный порядок", "https://i.imgur.com/Ny03N52.png", "rare", False),
    ("🔁 Showed Up Again", "Ты вернулся к задаче, даже если не хотел", "https://i.imgur.com/ltK1P5R.png", "rare", False),
    ("⏳ No Zero Day", "Ты не допустил нуля. Уважение", "https://i.imgur.com/ybxzXYo.png", "rare", False),
    
    ("🔒 Deep Work Mode", "Ты провёл 2 часа в глубокофокусной работе", "https://i.imgur.com/I87h0ji.png", "epic", False),
    ("🌊 Flow State", "Ты вошёл в поток. Это не часто случается", "https://i.imgur.com/KYYuUik.png", "epic", False),
    ("📈 Momentum Unlocked", "Ты начал серию — теперь только ускорение", "https://i.imgur.com/vVnGLRL.png", "epic", False),
    ("📚 Weekly Learner", "Ты завершил неделю с обучением каждый день", "https://i.imgur.com/z28dx3q.png", "epic", False),
    
    ("🔥 Streak Demon", "Ты держишь серию 🔥 Это уровень", "https://i.imgur.com/lF3r3pK.png", "legendary", True),
    ("🏔 Mind Over Matter", "Ты сделал то, что не хотелось. Уважение", "https://i.imgur.com/g4fxCJ3.png", "legendary", True),
    ("🧘 Master of Stillness", "Ты освоил тишину и спокойствие", "https://i.imgur.com/T4P7k8F.png", "legendary", True),
    ("🥇 Gold Routine", "Ты прожил идеальный день", "https://i.imgur.com/mZgF8v2.png", "legendary", True),
    ("👑 King of Consistency", "Ты держишь ритм недели. Это уровень босса", "https://i.imgur.com/0ldIlIN.png", "legendary", True),
]

import requests
from django.core.files.base import ContentFile
from core.shop.models import IconItem

def create_stikers():
    for name, desc, url, rarity, is_donation in stickers:
        image_resp = requests.get(url)
        item = IconItem(
            name=name,
            description=desc,
            price={"common": 150, "rare": 400, "epic": 800, "legendary": 200}[rarity],
            rarity=rarity,
            is_donation_only=is_donation
        )
        item.image.save(f"{name.replace(' ', '_')}.png", ContentFile(image_resp.content), save=True)
        item.save()

# def main():
#     create_stikers()

# if __name__ == '__main__':
#     main()