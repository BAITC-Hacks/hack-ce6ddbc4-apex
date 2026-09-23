# Tandau — бриф на 10 фирменных изображений

**Редакция 2.0 · 23 сентября 2026 · Пакет для генерации и передачи в интерфейс**

Нужно подготовить **ровно 10 отдельных изображений** с именами файлов из этого документа. Каждый английский промпт ниже можно передать генератору целиком. Все десять изображений сейчас **запрошены и ожидаются**: текст брифа, композиционная схема или слот на странице дизайнбука не считаются готовым изображением.

Выбранная насыщенная синяя волна уже доступна и остаётся текущим фоном. Изображение № 01 — необязательная новая версия в той же системе, а не повод заменить выбранный фон до просмотра результата. Остальные девять изображений образуют собственную предметную коллекцию Tandau. Они не являются изображениями реальных подрядчиков, площадок или оборудования.

## Общая художественная система

**Характер:** точность, спокойствие, дорогая предметная съёмка, ясность выбора. Впечатление создают материал, пропорция, свет и свободное пространство. Не добавлять декоративные элементы для заполнения кадра.

**Материалы:** оптическое стекло кобальтового синего цвета `#2B5FE3` и сатинированный алюминий. Допустимы небольшие тёмно-синие детали `#0E1626`. На одном объекте не больше двух доминирующих материалов. Насыщенный цвет собирается в одной смысловой части.

**Геометрия:** прямые плоскости, тонкие профили, точные соединения. Допустима маленькая технологическая фаска, которая ловит свет; недопустимы надутые формы и мягкие подушкообразные края. Волна — единственная намеренно текучая форма этой коллекции. Её пластика не переносится в геометрию кнопок и контейнеров.

**Камера и свет:** у девяти предметов общая ортографическая перспектива в три четверти, около 25° сверху. Большой мягкий источник слева сверху, слабое холодное заполнение справа. Контактная тень едва заметная и сохраняет прозрачность. Без чёрной студии, сильного свечения и случайных разноцветных бликов.

**Композиция:** один объект или одна простая связанная группа. Основная масса находится в центре. Вокруг не менее 14% свободного поля с каждой стороны, чтобы объект безопасно масштабировался. Силуэт и смысл должны читаться при показе в 96–128 px.

**Формат:** № 01 — `2560 × 1600`, RGB PNG с готовым светлым фоном. № 02–10 — `1600 × 1600`, RGBA PNG с настоящим альфа-каналом. Цветовое пространство sRGB. Имена только строчными латинскими буквами с дефисами, строго по таблице. Не добавлять номер версии, пробелы и суффикс `final` к финальному имени.

**Текст и интерфейс:** не рисовать буквы, цифры, названия, логотипы, валюту, таблицы с данными, интерфейсные скриншоты и водяные знаки. Тексты, цены, дата и интерактивные состояния всегда создаются средствами интерфейса. Единственное разрешённое смысловое начертание в изображениях — простая галочка в № 10.

### Общий negative prompt

> text, letters, numbers, logos, watermark, interface screenshot, people, hands, coins, currency symbols, cartoon, toy, inflated plastic, gummy material, excessive rounding, rounded cushion, sparkles, lens flare, rainbow gradients, confetti, busy environment, fake transparency checkerboard, white rectangle behind isolated object, certification seal, fake rating, blurry edges, cropped object

Для № 01 отсутствие прозрачности — намеренное требование, поэтому ограничения про белый прямоугольник и прозрачность к фону не относятся. Готовые промпты уже учитывают различия между фоном и предметами.

## Очерёдность и имена файлов

`P1` — сначала: основной смысл продукта и критические состояния. `P2` — после первой согласованной партии: дополнительные поверхности и необязательная новая волна. Приоритет не означает, что остальные изображения можно исключить из заказанных десяти.

| № | Имя файла | Смысл | Размер | Приоритет |
| --- | --- | --- | --- | --- |
| 01 | `tandau-hero-wave.png` | Главная синяя волна | 2560 × 1600 | P2 |
| 02 | `tandau-choice-stack.png` | Три варианта — один выбор | 1600 × 1600 | P1 |
| 03 | `tandau-event-stage.png` | Сцена мероприятия | 1600 × 1600 | P1 |
| 04 | `tandau-calendar-block.png` | Блок даты | 1600 × 1600 | P1 |
| 05 | `tandau-budget-frame.png` | Рамка бюджета | 1600 × 1600 | P1 |
| 06 | `tandau-match-lens.png` | Линза объяснения | 1600 × 1600 | P1 |
| 07 | `tandau-shortlist-marker.png` | Метка сохранённого варианта | 1600 × 1600 | P2 |
| 08 | `tandau-empty-search.png` | Открытая рамка поиска | 1600 × 1600 | P1 |
| 09 | `tandau-account-vault.png` | Папка личного пространства | 1600 × 1600 | P2 |
| 10 | `tandau-complete-check.png` | Завершённый шаг | 1600 × 1600 | P2 |


## 01. Главная синяя волна

**Файл:** `tandau-hero-wave.png` · **2560 × 1600 px** · **RGB, светлый фон, без прозрачности** · **P2**

Насыщенная синяя стеклянная волна для крупных брендовых композиций. Широкая светлая область остаётся свободной под заголовок.

**Зачем:** Дать продукту узнаваемый масштабный образ без текстовых обещаний. Волна — единственное намеренно текучее исключение в системе строгих плоскостей.

**Композиция:** Светлая область занимает верхнюю левую часть; активная синяя форма — нижнюю правую. Главный изгиб должен сохраняться при кропе 16:9 и 3:2. Изображение не содержит стеклянных плиток, кнопок и текста.

**Где использовать:** Лендинг и титульная композиция дизайнбука. Необязательная будущая замена: выбранный пользователем текущий фон остаётся до отдельного решения.

### Готовый промпт

```text
Create a premium abstract brand background for Tandau, an event-contractor selection product. A single broad ribbon of clear optical glass flows diagonally from the lower left toward the upper right and folds once with an elongated, controlled curve. The glass is vivid cobalt blue #2B5FE3 along its thick edges and almost colorless across thin surfaces, with deep navy refraction and clean icy blue highlights. The composition feels like a photographed architectural glass sculpture: realistic sharp glass boundaries, restrained caustics, excellent material depth and elegant tension. Keep the upper-left 45 percent of the frame predominantly clean white to pale cool gray for a separate HTML heading; concentrate the richest blue detail in the lower-right half. Use soft daylight studio illumination with a bright neutral background and no dark environment. Produce a 2560 by 1600 pixel RGB PNG with no transparency. This is a background only, without floating tiles or UI. No text, letters, numbers, logos, watermark, icons, people, hands, rounded cards, spheres, inflated plastic, confetti, sparkles, lens flare, rainbow gradients or decorative borders. Do not embed shadows belonging to any foreground card. Preserve broad calm regions that remain useful after horizontal or vertical cropping.
```

**Проверка результата:** Фон выглядит насыщенным синим стеклом, а не тканью или дымом. Текст можно разместить на светлой области без тяжёлой маски. Никакие содержательные части не обрезаются при двух рабочих кропах.


## 02. Три варианта — один выбор

**Файл:** `tandau-choice-stack.png` · **1600 × 1600 px** · **RGBA, настоящий прозрачный фон** · **P1**

Три тонкие архитектурные пластины; одна синяя немного выдвинута вперёд. Главный символ осознанного выбора.

**Зачем:** Показать выбор из ограниченного числа вариантов. Объект не сообщает, что три результата будут найдены при каждом запросе.

**Композиция:** Ровно три одинаковые пластины. Выдвинутая синяя плоскость выделяется положением и материалом, остальные остаются нейтральными. Наклон у группы общий.

**Где использовать:** Блок «До трёх подрядчиков» на лендинге; титульная часть раздела результатов; крупная графика пустого рабочего пространства до ввода условий.

### Готовый промпт

```text
Use the same studio art direction throughout the Tandau collection: precise planar forms, cobalt blue #2B5FE3 optical glass and satin brushed aluminum, deep navy #0E1626 details used sparingly. Hard engineered edges with tiny realistic bevels, optical refraction, subtle material imperfections, restrained reflections. Orthographic three-quarter view, approximately 25 degrees elevation, soft large key light from upper left, faint cool fill from right, consistent clean product-photography lighting. Center the object with at least 14 percent clear padding on all sides; keep the silhouette legible at 96 pixels. Export a single isolated object group as a real transparent-background RGBA PNG, 1600 by 1600 pixels, with a very subtle translucent contact shadow only. No text, letters, numbers, logos, watermark, interface screenshots, people, hands, coins, currency symbols, cartoon styling, inflated plastic, gummy material, excessive rounding, sparkles, lens flare, rainbow gradients, confetti, busy environment, checkerboard background or white rectangular backdrop. Create three thin upright rectangular slabs in one aligned group, representing a shortlist of up to three contractors. Two slabs are satin silver with lightly translucent white glass faces; the third slab is deep cobalt optical glass and sits slightly forward by one slab thickness. All three have identical dimensions and disciplined almost-square corners with tiny bevels. Show a slim offset between slabs so all three are countable and the selected slab is clear. The arrangement is a precise tabletop architectural model, not a pile of playing cards or a device screen. Do not place checkmarks, badges, portrait shapes or any graphic marks on the slabs. Give the blue slab a refined edge highlight and allow light to pass through it. Keep the geometry simple enough to read as three options rather than a staircase.
```

**Проверка результата:** На размере 96 px различимы ровно три варианта и один акцент. Нет пустых экранов устройств, карточных мастей и вымышленных интерфейсных надписей.


## 03. Сцена мероприятия

**Файл:** `tandau-event-stage.png` · **1600 × 1600 px** · **RGBA, настоящий прозрачный фон** · **P1**

Миниатюрная прямоугольная сцена с тонкой синей задней плоскостью и двумя строгими световыми стойками.

**Зачем:** Привязать бренд к организации мероприятий, а не к абстрактной аналитике. Иллюстрация обозначает контекст запроса, не конкретную категорию услуг.

**Композиция:** Один подиум, одна задняя плоскость, две тонкие стойки. Главная масса горизонтальна, стекло даёт вертикальный противовес. Без россыпи реквизита.

**Где использовать:** Начало брифа мероприятия и блок сценариев на лендинге. Не использовать как фото реального объекта или оборудования подрядчика.

### Готовый промпт

```text
Use the same studio art direction throughout the Tandau collection: precise planar forms, cobalt blue #2B5FE3 optical glass and satin brushed aluminum, deep navy #0E1626 details used sparingly. Hard engineered edges with tiny realistic bevels, optical refraction, subtle material imperfections, restrained reflections. Orthographic three-quarter view, approximately 25 degrees elevation, soft large key light from upper left, faint cool fill from right, consistent clean product-photography lighting. Center the object with at least 14 percent clear padding on all sides; keep the silhouette legible at 96 pixels. Export a single isolated object group as a real transparent-background RGBA PNG, 1600 by 1600 pixels, with a very subtle translucent contact shadow only. No text, letters, numbers, logos, watermark, interface screenshots, people, hands, coins, currency symbols, cartoon styling, inflated plastic, gummy material, excessive rounding, sparkles, lens flare, rainbow gradients, confetti, busy environment, checkerboard background or white rectangular backdrop. Create a miniature contemporary event stage as a refined architectural scale model. Use one low rectangular brushed-aluminum podium, one freestanding upright cobalt glass backdrop behind it, and two very thin navy lighting uprights arranged symmetrically at the rear corners. The glass backdrop is a single uninterrupted plane, with no screen content. Use exact proportions, crisp planar geometry and an elegant restrained silhouette. The podium should be wider than it is deep, with a narrow reveal along its edge. Include no microphone, musical instrument, speaker logo, audience, performer, chairs, drapery or decorative floral objects. Do not turn the stage into a concert arena or exhibition building. Convey the idea of an organized event through this one calm, precise model rather than through an abundance of equipment.
```

**Проверка результата:** Объект читается как небольшая сцена. Нет людей, известных площадок и узнаваемого оборудования. При уменьшении стойки не превращаются в световой шум.


## 04. Блок даты

**Файл:** `tandau-calendar-block.png` · **1600 × 1600 px** · **RGBA, настоящий прозрачный фон** · **P1**

Строгий настольный календарный блок с гравированной сеткой без цифр; одна ячейка выделена синим стеклом.

**Зачем:** Обозначить параметр даты. Единственная акцентная ячейка обозначает выбранное условие, а не гарантированную доступность исполнителя.

**Композиция:** Один почти фронтальный календарный блок; сетка без подписей; одна вставка. Сдержанная перспектива сохраняет понятную форму календаря.

**Где использовать:** Шаг выбора даты в брифе; пояснение условия даты. Не заменяет настоящий интерактивный календарь.

### Готовый промпт

```text
Use the same studio art direction throughout the Tandau collection: precise planar forms, cobalt blue #2B5FE3 optical glass and satin brushed aluminum, deep navy #0E1626 details used sparingly. Hard engineered edges with tiny realistic bevels, optical refraction, subtle material imperfections, restrained reflections. Orthographic three-quarter view, approximately 25 degrees elevation, soft large key light from upper left, faint cool fill from right, consistent clean product-photography lighting. Center the object with at least 14 percent clear padding on all sides; keep the silhouette legible at 96 pixels. Export a single isolated object group as a real transparent-background RGBA PNG, 1600 by 1600 pixels, with a very subtle translucent contact shadow only. No text, letters, numbers, logos, watermark, interface screenshots, people, hands, coins, currency symbols, cartoon styling, inflated plastic, gummy material, excessive rounding, sparkles, lens flare, rainbow gradients, confetti, busy environment, checkerboard background or white rectangular backdrop. Create one slim, freestanding calendar block with a satin aluminum rectangular face and a small cobalt glass base. The face has an orderly shallow engraved seven-column, five-row grid, without any numbers, letters, month name or day labels. Mark exactly one cell near the center using a flush cobalt optical-glass inset, not a raised button. Include two small simple rectangular binding bridges at the top, keeping their shape engineered rather than circular and playful. The face is upright with only a slight backward lean. Make the grid subtle enough to remain secondary to the strong calendar silhouette. This is a conceptual date-selection object, not a screenshot or a real availability calendar. Avoid loose calendar sheets, checkmarks, clocks, bells, celebration details and stacked date cards.
```

**Проверка результата:** Нет случайных псевдоцифр и текста. Выделена ровно одна ячейка. Сетка не муарит при размере 128 px. Металл и стекло различимы.


## 05. Рамка бюджета

**Файл:** `tandau-budget-frame.png` · **1600 × 1600 px** · **RGBA, настоящий прозрачный фон** · **P1**

Тонкая металлическая рамка с синей стеклянной планкой внутри: обозначение заданного бюджета без денег и платёжных символов.

**Зачем:** Показать ограничение, внутри которого принимается решение. Реальные суммы, валюта и обязательное слово «от» остаются живым текстом интерфейса.

**Композиция:** Рамка задаёт доступный диапазон, горизонтальная планка занимает его часть. Свободное место справа обязательно. Все плоскости чистые.

**Где использовать:** Шаг бюджета и объяснение «в пределах бюджета». Не использовать как обозначение оплаты или точного коммерческого предложения.

### Готовый промпт

```text
Use the same studio art direction throughout the Tandau collection: precise planar forms, cobalt blue #2B5FE3 optical glass and satin brushed aluminum, deep navy #0E1626 details used sparingly. Hard engineered edges with tiny realistic bevels, optical refraction, subtle material imperfections, restrained reflections. Orthographic three-quarter view, approximately 25 degrees elevation, soft large key light from upper left, faint cool fill from right, consistent clean product-photography lighting. Center the object with at least 14 percent clear padding on all sides; keep the silhouette legible at 96 pixels. Export a single isolated object group as a real transparent-background RGBA PNG, 1600 by 1600 pixels, with a very subtle translucent contact shadow only. No text, letters, numbers, logos, watermark, interface screenshots, people, hands, coins, currency symbols, cartoon styling, inflated plastic, gummy material, excessive rounding, sparkles, lens flare, rainbow gradients, confetti, busy environment, checkerboard background or white rectangular backdrop. Create a precise rectangular brushed-aluminum frame, like a small architectural measuring instrument, with a single cobalt optical-glass horizontal bar suspended inside. The bar occupies roughly two thirds of the inner width and ends at a crisp vertical edge, leaving visible empty space to the right. Add one extremely thin neutral vertical divider near the far-right interior edge to suggest a defined limit. Keep all surfaces completely blank, with no tick marks, numerals, currency symbols, coins, banknotes or price tags. The frame is slim and upright, with square corners and small realistic bevels. Use a small stable base that does not dominate the composition. This object should communicate a bounded allowance and thoughtful allocation, not payment, investment, wealth, trading or a growth chart. No arrows and no gauges with needles.
```

**Проверка результата:** Нет монет, купюр, процентов и стрелок роста. Объект не похож на банковскую карту. В малом размере видна граница и содержимое внутри неё.


## 06. Линза объяснения

**Файл:** `tandau-match-lens.png` · **1600 × 1600 px** · **RGBA, настоящий прозрачный фон** · **P1**

Прямоугольная оптическая линза над тремя ровными информационными пластинами. Образ прозрачного объяснения выбора.

**Зачем:** Поддержать понятность объяснений. Линза помогает рассмотреть данные; она не означает, что система знает недоступные факты об исполнителе.

**Композиция:** Линза расположена на небольшом расстоянии над тремя параллельными пластинами. Одна синяя пластина связывает этот объект с символом выбора.

**Где использовать:** Раздел «Почему в подборке», объяснение условий и сведения об источнике данных. Не является знаком проверки личности.

### Готовый промпт

```text
Use the same studio art direction throughout the Tandau collection: precise planar forms, cobalt blue #2B5FE3 optical glass and satin brushed aluminum, deep navy #0E1626 details used sparingly. Hard engineered edges with tiny realistic bevels, optical refraction, subtle material imperfections, restrained reflections. Orthographic three-quarter view, approximately 25 degrees elevation, soft large key light from upper left, faint cool fill from right, consistent clean product-photography lighting. Center the object with at least 14 percent clear padding on all sides; keep the silhouette legible at 96 pixels. Export a single isolated object group as a real transparent-background RGBA PNG, 1600 by 1600 pixels, with a very subtle translucent contact shadow only. No text, letters, numbers, logos, watermark, interface screenshots, people, hands, coins, currency symbols, cartoon styling, inflated plastic, gummy material, excessive rounding, sparkles, lens flare, rainbow gradients, confetti, busy environment, checkerboard background or white rectangular backdrop. Create a single rectangular thick optical-glass inspection lens positioned slightly above three thin, parallel, horizontally aligned data slabs. Use two satin aluminum slabs and one cobalt glass slab. Each slab carries only two shallow geometric grooves, no writing, numbers, icons or charts. The lens is a clear rectangular prism with a very subtle cobalt tint and a narrow brushed-aluminum strip on one edge; it has no handle and is not a magnifying-glass icon. Through the lens, show a physically plausible slight magnification or refraction of the grooves beneath it. Keep all slabs in one calm aligned stack with clear spacing. The lens should feel like a precise optical tool used to see a choice clearly. Avoid robot eyes, magical beams, scanning lasers, neural networks, floating particles and complex science-fiction machinery.
```

**Проверка результата:** Преломление умеренное и физически правдоподобное. Нет лица, глаза, надписей и магического свечения. Линза имеет прямоугольную, а не круглую форму.


## 07. Метка сохранённого варианта

**Файл:** `tandau-shortlist-marker.png` · **1600 × 1600 px** · **RGBA, настоящий прозрачный фон** · **P2**

Тонкая синяя стеклянная закладка с чётким V-образным вырезом на одной алюминиевой пластине.

**Зачем:** Отделить сохранение варианта от его подтверждения и бронирования. Изображение относится к намерению вернуться к выбору.

**Композиция:** Одна нейтральная пластина и одна закладка. V-образный вырез должен быть виден, но не превращать объект в наградную ленту.

**Где использовать:** Пустое избранное, вступление к сохранённым вариантам и пояснение функции короткого списка. Не заменяет пиктограмму кнопки.

### Готовый промпт

```text
Use the same studio art direction throughout the Tandau collection: precise planar forms, cobalt blue #2B5FE3 optical glass and satin brushed aluminum, deep navy #0E1626 details used sparingly. Hard engineered edges with tiny realistic bevels, optical refraction, subtle material imperfections, restrained reflections. Orthographic three-quarter view, approximately 25 degrees elevation, soft large key light from upper left, faint cool fill from right, consistent clean product-photography lighting. Center the object with at least 14 percent clear padding on all sides; keep the silhouette legible at 96 pixels. Export a single isolated object group as a real transparent-background RGBA PNG, 1600 by 1600 pixels, with a very subtle translucent contact shadow only. No text, letters, numbers, logos, watermark, interface screenshots, people, hands, coins, currency symbols, cartoon styling, inflated plastic, gummy material, excessive rounding, sparkles, lens flare, rainbow gradients, confetti, busy environment, checkerboard background or white rectangular backdrop. Create one slim cobalt optical-glass bookmark wedge resting vertically over the upper edge of a single satin brushed-aluminum rectangular slab. The bookmark is flat and narrow, with parallel straight sides and a precise shallow V-shaped notch at its lower end. Its top is straight, not a loop. Allow enough overlap to make the connection between marker and slab clear. The aluminum slab is completely blank and nearly square, with a small engineered bevel. Keep the material depth visible, but do not make the bookmark thick or inflated. The composition should suggest setting aside a promising option for later consideration. No heart, star, checkmark, medal, ribbon bow, paper pages, text, profile silhouette or smartphone body. The marker itself is the only saturated blue element.
```

**Проверка результата:** Не выглядит как медаль, лайк или подтверждённая бронь. Силуэт закладки узнаваем при размере 96 px. Нет вторичного синего декора.


## 08. Открытая рамка поиска

**Файл:** `tandau-empty-search.png` · **1600 × 1600 px** · **RGBA, настоящий прозрачный фон** · **P1**

Открытая металлическая рамка с аккуратным разрывом и маленькой синей направляющей. Спокойный образ для отсутствия результатов.

**Зачем:** Показать, что поиск можно изменить. Пустое состояние не должно выглядеть как наказание или системная ошибка.

**Композиция:** Пустота внутри рамки — главный элемент. Разрыв находится сверху справа и имеет ровные края. Маленькая направляющая задаёт продолжение поиска.

**Где использовать:** Нет подходящих результатов и нет категории в каталоге города. Подпись и действие всегда объясняют конкретный исход.

### Готовый промпт

```text
Use the same studio art direction throughout the Tandau collection: precise planar forms, cobalt blue #2B5FE3 optical glass and satin brushed aluminum, deep navy #0E1626 details used sparingly. Hard engineered edges with tiny realistic bevels, optical refraction, subtle material imperfections, restrained reflections. Orthographic three-quarter view, approximately 25 degrees elevation, soft large key light from upper left, faint cool fill from right, consistent clean product-photography lighting. Center the object with at least 14 percent clear padding on all sides; keep the silhouette legible at 96 pixels. Export a single isolated object group as a real transparent-background RGBA PNG, 1600 by 1600 pixels, with a very subtle translucent contact shadow only. No text, letters, numbers, logos, watermark, interface screenshots, people, hands, coins, currency symbols, cartoon styling, inflated plastic, gummy material, excessive rounding, sparkles, lens flare, rainbow gradients, confetti, busy environment, checkerboard background or white rectangular backdrop. Create a minimal upright rectangular brushed-aluminum frame with an intentional open gap in the upper-right corner. Place one small cobalt optical-glass guide block just outside this gap, aligned with the frame rather than floating randomly. The interior is completely empty and transparent. The frame has precise flat faces, a thin stable foot and nearly square corners with tiny realistic bevels. Convey an unfinished but approachable space that can be adjusted, without distress or failure. Keep the composition balanced, light and calm. Do not include a magnifying glass, question mark, exclamation mark, cross, broken chain, trash bin, sad face, warning triangle, lock, crack, shattered glass or scattered pieces. The gap is designed and clean, never damaged. Leave generous breathing room around the object.
```

**Проверка результата:** Рамка выглядит открытой намеренно, а не сломанной. Отсутствуют тревожные символы. Внутри нет случайно сгенерированных объектов и декоративного мусора.


## 09. Папка личного пространства

**Файл:** `tandau-account-vault.png` · **1600 × 1600 px** · **RGBA, настоящий прозрачный фон** · **P2**

Тонкая алюминиевая папка с синей стеклянной обложкой и небольшим точным замком-ползунком.

**Зачем:** Связать аккаунт с организацией собственных подборок и истории. Иллюстрация не вводит новую функцию и не обещает защиту, которую нельзя подтвердить.

**Композиция:** Папка имеет тонкий профиль; одна внутренняя плоскость видна через небольшой зазор. Стекло и металл связаны маленьким плоским зажимом.

**Где использовать:** Боковая композиция входа и регистрации, вступление к кабинету. Не использовать как доказательство сертификации или абсолютной безопасности.

### Готовый промпт

```text
Use the same studio art direction throughout the Tandau collection: precise planar forms, cobalt blue #2B5FE3 optical glass and satin brushed aluminum, deep navy #0E1626 details used sparingly. Hard engineered edges with tiny realistic bevels, optical refraction, subtle material imperfections, restrained reflections. Orthographic three-quarter view, approximately 25 degrees elevation, soft large key light from upper left, faint cool fill from right, consistent clean product-photography lighting. Center the object with at least 14 percent clear padding on all sides; keep the silhouette legible at 96 pixels. Export a single isolated object group as a real transparent-background RGBA PNG, 1600 by 1600 pixels, with a very subtle translucent contact shadow only. No text, letters, numbers, logos, watermark, interface screenshots, people, hands, coins, currency symbols, cartoon styling, inflated plastic, gummy material, excessive rounding, sparkles, lens flare, rainbow gradients, confetti, busy environment, checkerboard background or white rectangular backdrop. Create a slim premium personal-document folder as a single engineered object: a brushed-aluminum rear panel, a translucent cobalt optical-glass front panel and a very small flush rectangular clasp along the right edge. The folder is upright and slightly open by only a few degrees, revealing one blank pale silver inner sheet. Use a modest offset tab on the upper left of the back panel to make the folder recognizable. The clasp is a simple mechanical slider without a padlock shape, keyhole, numeric keypad or indicator light. Every surface is blank. The object should convey an organized private workspace, not a bank vault, cybersecurity certification or impenetrable security. Avoid shields, fingerprints, face scans, keys, chains, money, heavy safe doors, digital screens and multiple flying sheets.
```

**Проверка результата:** Читается как папка, а не сейф или ноутбук. Нет банковских или биометрических символов. Тонкий объект не выглядит тяжёлым и громоздким.


## 10. Завершённый шаг

**Файл:** `tandau-complete-check.png` · **1600 × 1600 px** · **RGBA, настоящий прозрачный фон** · **P2**

Почти квадратная плоская плитка синего стекла с тонкой белой галочкой, утопленной в поверхность.

**Зачем:** Дать спокойное подтверждение действия. Семантика задаётся соседним текстом, а не произвольным употреблением галочки.

**Композиция:** Одна плоская плитка и одна тонкая галочка. Скругление ограничено технологической фаской. Сильный блик не перекрывает смысловой знак.

**Где использовать:** Завершённый шаг брифа или локально успешное действие. Не ставить как знак верификации подрядчика или подтверждения бронирования.

### Готовый промпт

```text
Use the same studio art direction throughout the Tandau collection: precise planar forms, cobalt blue #2B5FE3 optical glass and satin brushed aluminum, deep navy #0E1626 details used sparingly. Hard engineered edges with tiny realistic bevels, optical refraction, subtle material imperfections, restrained reflections. Orthographic three-quarter view, approximately 25 degrees elevation, soft large key light from upper left, faint cool fill from right, consistent clean product-photography lighting. Center the object with at least 14 percent clear padding on all sides; keep the silhouette legible at 96 pixels. Export a single isolated object group as a real transparent-background RGBA PNG, 1600 by 1600 pixels, with a very subtle translucent contact shadow only. No text, letters, numbers, logos, watermark, interface screenshots, people, hands, coins, currency symbols, cartoon styling, inflated plastic, gummy material, excessive rounding, sparkles, lens flare, rainbow gradients, confetti, busy environment, checkerboard background or white rectangular backdrop. Create one flat nearly square cobalt optical-glass tile with a precise thin white ceramic checkmark inset flush into its front face. The tile has hard planar edges and very small bevels, not rounded cushion corners. Make the checkmark geometrically simple, centered and comfortably padded, occupying about 40 percent of the face width. Show the tile standing with a slight backward lean on a tiny satin-aluminum support that is almost hidden. The glass is transparent enough to show edge depth but saturated enough for the white inset to remain clear. This is a calm visual sign for completing a local user step, not a certificate or award. Do not add a circle, shield, seal, ribbon, medal, star, confetti, sparkle, glow, percentage, text, logo or extra tiles.
```

**Проверка результата:** Галочка видна на светлом и тёмном фоне при размере 96 px. Нет наградных и сертификационных мотивов. Стекло остаётся плоским, без формы подушки.


## Передача файлов

Передайте десять PNG с точными именами из таблицы. Можно передавать партиями: сначала № 02, 03, 04, 05, 06 и 08; затем № 07, 09, 10 и необязательную новую версию № 01. Промпты не требуют добавлять надписи в саму картинку.

Если генератор не умеет настоящий прозрачный фон, сообщите об этом вместе с результатом. Не выдавайте белый фон или изображённую шахматную сетку за прозрачность. Лучше сохранить исходник без потери качества, чем удалять фон с рваными краями. Экспорт для интерфейса принимается только после проверки альфа-канала.

Не уменьшайте исходные изображения перед передачей и не прогоняйте их через мессенджерное сжатие. Формат для первого просмотра — тот же PNG, что будет использоваться как мастер. Размер файла не важнее чистого контура; облегчённые WebP/AVIF и размеры под экран готовятся при интеграции отдельно, сохраняя мастер.

## Проверка всей серии

1. В наборе ровно десять файлов с нужными именами и размерами; все открываются без ошибок.
2. Девять предметов принадлежат одной системе света, камеры, кобальтового стекла и сатинированного алюминия.
3. Альфа-канал настоящей прозрачности проверен на белом, светло-сером и тёмно-синем фоне; вокруг объектов нет белой каймы.
4. Каждый предмет остаётся различимым при размере 96 px и выглядит чисто при показе 320 px. Никакой объект не обрезан границами изображения.
5. Нет букв, псевдотекста, валютных знаков, логотипов, людей и водяных знаков. В № 10 допускается только оговорённая галочка.
6. Нет визуальных обещаний рейтинга, проверенной личности, точной цены, оплаты или подтверждённой брони.
7. В серии выдержаны жёсткие плоскости и маленькие фаски. Круглые надутые формы не маскируются под премиальное стекло.
8. Волна сохраняет свободное место под живой текст и сравнивается с уже выбранным фоном перед заменой.

## Правила размещения в Tandau

Объект не должен быть крупнее действия или результата, который поясняет. На рабочем экране подбора максимум одна крупная иллюстрация на видимую область; карточки подрядчиков остаются преимущественно текстовыми. Не ставить 3D-объекты внутрь каждого поля, кнопки и бейджа.

В кнопках, предупреждениях и навигации используются простые векторные пиктограммы. Предметная графика отвечает за смысл раздела и характер бренда. Минимальные рабочие размеры: 96 px для предмета, 160–240 px для акцентной композиции. Смысловое содержание всегда повторяется текстом.

Если соседний заголовок уже объясняет изображение, использовать пустой `alt=""`, чтобы не повторять его для программы чтения с экрана. Если изображение несёт самостоятельный смысл, короткий alt описывает объект и действие, без слов «картинка» и без заявления о реальном исполнителе. В № 01 фон декоративный и всегда имеет пустой alt.

Не загружать все десять больших мастеров при открытии рабочего экрана. При интеграции подобрать размер под область вывода, задать ширину и высоту, отложить загрузку нижних секций и сохранить прозрачность у производных форматов. Текущий файл с брифами — спецификация, а не список уже доступных изображений.

Машиночитаемая версия десяти запросов: [`asset-briefs.json`](../app/static/assets/tandau/asset-briefs.json). Страница дизайнбука использует эти данные для списка ожидаемой графики, копирования промптов и проверки точных имён.
