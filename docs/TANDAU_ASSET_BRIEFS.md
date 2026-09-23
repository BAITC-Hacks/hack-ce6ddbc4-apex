# Tandau — 16 предметных изображений

**Редакция 3.0 · 23 сентября 2026**

Нужно создать **16 отдельных изображений** для Tandau. Все шестнадцать пока ожидаются от автора генерации. Промпт, схема и карточка в дизайнбуке не являются готовым изображением. Сначала согласуем три калибровочных предмета, затем переносим их свет, материал и масштаб на всю серию.

Новая коллекция строится на узнаваемых предметах организации мероприятий. Основной цвет предметов — **чёрный #000000**. Дополнительные материалы — сатинированный хром и небольшие непрозрачные кобальтовые детали #2B5FE3. Волны, синие стеклянные ленты и прозрачные абстрактные фигуры в этот пакет не входят. Старые графические решения не служат визуальным стандартом для новой серии.

## Сначала три калибровочных изображения

Сгенерируйте в первую очередь эти три файла по полным промптам ниже.

1. `tandau-microphone.png` проверяет чёрный металл, хромированную сетку и округлую функциональную форму.
2. `tandau-camera.png` проверяет сложный предмет, точные стыки и читаемость при уменьшении.
3. `tandau-calendar.png` проверяет светлую бумагу, тонкие детали и один непрозрачный синий акцент.

Во всех трёх должны совпасть направление света, угол камеры, плотность чёрного и масштаб предмета. После согласования используйте их как визуальные образцы для оставшихся тринадцати изображений, если генератор поддерживает работу с референсами. Не добавляйте эти образцы в итоговый кадр как вторые объекты.

## Общая художественная система

### Предметы и смысл

Каждая иконка показывает один узнаваемый предмет или простую связанную группу. Микрофон сохраняет цилиндрическую рукоять и металлическую сетку; цветы остаются цветами; камера имеет объектив и рукоять. Не превращать все категории в одинаковые кубы, плитки и рамки.

Изображения представляют тип услуги или действие интерфейса. Они не изображают оборудование конкретного подрядчика, реальную площадку, его портрет или подтверждённое бронирование. Имена, цены, даты и объяснения выводятся текстом в интерфейсе.

### Цвет и материал

Матовые основные поверхности имеют нейтральный чёрный базовый цвет **#000000**. Физически правдоподобные серые отражения и грани допустимы и нужны для объёма. Запрещены тёмно-синий подтон, цветной свет, синий рефлекс на всей поверхности и окрашивание чёрного в navy.

Хром сатинированный, со сдержанными широкими бликами. Он подчёркивает реальные крепления, ободки и соединения. Не превращать металлические детали в зеркало с пёстрым окружением.

Кобальт **#2B5FE3** непрозрачный и лаковый. Обычно он занимает менее 8% видимой площади предмета. Никакого прозрачного синего стекла и свечения. Нейтральная тёмная оптика камеры и прожектора допустима как часть реального предмета.

Бумага светлая, без синевы. У флористики допустимы натуральные белые лепестки и тёмно-зелёные стебли. Эти предметные материалы не заменяются металлом ради единообразия.

### Форма и свет

Геометрия точная и физически возможная. Небольшие фаски помогают читать грани. Округления соответствуют реальному предмету; надутая пластмасса, мягкие подушки и игрушечные пропорции не допускаются.

Общая камера показывает предмет в три четверти с горизонтальным поворотом 30° и высотой 20° над плоскостью. Используется ортографическая или длиннофокусная перспектива без широкоугольных искажений. Предметные различия допускают поворот самого объекта, но не смену общего света.

Большой мягкий источник находится слева сверху; справа работает слабое нейтральное заполнение. Контактная тень лёгкая и прозрачная. Нет жёсткого чёрного пятна, неонового обода, пыльных лучей, искр и частиц.

### Экспорт

Hero `tandau-production-desk.png` имеет размер **2400 × 1600 px**, цветовое пространство sRGB, формат RGB PNG и готовую светлую поверхность #F5F5F5. Текст и кнопки не запекаются в изображение.

Остальные пятнадцать иконок имеют размер **1600 × 1600 px**, sRGB, формат RGBA PNG с настоящим альфа-каналом. Предмет полностью помещается в кадре. По всем краям остаётся не менее 14% свободного поля; важные детали не выходят за его пределы. Объект должен читаться при размере 96 px.

Шахматная сетка не должна быть нарисована внутри картинки. Белый прямоугольник вокруг предмета не является прозрачностью. Прозрачный экспорт нужно проверять на светлом, сером и чёрном фоне.

### Общие исключения

Никаких букв, псевдотекста, чисел, логотипов, водяных знаков, людей и рук. Не рисовать реальные интерфейсы, профили подрядчиков, фотографии событий, рейтинги и цены. Не добавлять волн, абстрактной воды, синего стекла, конфетти, искр, сияния и случайного реквизита.

Исключения для конкретных предметов описаны в промптах. В календаре нужна сетка без чисел, в брифе нужны простые линии без текста, а галочка является отдельным смысловым объектом.

## Файлы и очерёдность

`P1` нужен для главной композиции, категорий и первого сценария подбора. `P2` дополняет результаты, личные разделы и состояния. Все 16 файлов входят в заказанный пакет.

| № | Имя файла | Предмет | Размер | Приоритет |
| --- | --- | --- | --- | --- |
| 01 | `tandau-production-desk.png` | Продакшн мероприятия | 2400 × 1600 | P1 |
| 02 | `tandau-microphone.png` | Ведущий и звук | 1600 × 1600 | P1 |
| 03 | `tandau-camera.png` | Фотосъёмка | 1600 × 1600 | P1 |
| 04 | `tandau-video-camera.png` | Видеосъёмка | 1600 × 1600 | P1 |
| 05 | `tandau-stage-light.png` | Сценический свет | 1600 × 1600 | P1 |
| 06 | `tandau-venue.png` | Площадка мероприятия | 1600 × 1600 | P1 |
| 07 | `tandau-floral-arrangement.png` | Флористика и декор | 1600 × 1600 | P1 |
| 08 | `tandau-calendar.png` | Дата мероприятия | 1600 × 1600 | P1 |
| 09 | `tandau-budget.png` | Бюджет | 1600 × 1600 | P1 |
| 10 | `tandau-shortlist.png` | Короткий список | 1600 × 1600 | P2 |
| 11 | `tandau-comparison.png` | Сравнение вариантов | 1600 × 1600 | P2 |
| 12 | `tandau-brief.png` | Бриф мероприятия | 1600 × 1600 | P1 |
| 13 | `tandau-complete.png` | Шаг выполнен | 1600 × 1600 | P2 |
| 14 | `tandau-open-folder.png` | Пустой раздел | 1600 × 1600 | P2 |
| 15 | `tandau-keycard.png` | Личный доступ | 1600 × 1600 | P2 |
| 16 | `tandau-choice-tray.png` | Выбор из трёх | 1600 × 1600 | P2 |


## 01. Продакшн мероприятия

`tandau-production-desk.png` · 2400 × 1600 px · RGB PNG со светлым фоном · P1

Предметная композиция из микрофона, камеры, прожектора и папки брифа на светлой рабочей поверхности. Главная иллюстрация продукта.

### Предмет и задача

Связать первый экран с настоящей работой над мероприятием. Содержимое иллюстрации не является инвентарём конкретного подрядчика.

Ровно четыре предмета: один ручной микрофон, одна беззеркальная камера с объективом, один компактный сценический прожектор и одна закрытая папка брифа. Проводов и дополнительного реквизита нет.

### Композиция и материалы

Вся предметная группа находится в правых 48% кадра. Слева остаётся не менее 45% свободной светлой поверхности. Микрофон лежит по диагонали перед камерой; прожектор стоит справа; папка лежит за передним краем камеры.

Нейтральный матовый чёрный металл, сатинированный хром, мелкие непрозрачные кобальтовые детали. Поверхность фона тёплая светлая #F5F5F5.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Титульная композиция дизайнбука и hero лендинга. Текст и действия располагаются отдельно слева.

### Полный промпт для генерации

```text
Create a photorealistic still-life composition for the Tandau event-production website, 2400 by 1600 pixels, sRGB RGB PNG. The scene contains exactly four objects on a clean neutral off-white #F5F5F5 matte tabletop: one handheld microphone with a matte black cylindrical handle and satin chrome mesh grille; one compact black mirrorless camera with a single lens and a narrow chrome lens rim; one small black event spotlight in a mechanical yoke with chrome pivots; and one closed slim black event-brief folio with a small chrome clip. No other props. Arrange the four objects as a coherent working group in the right 48 percent of the image, with slight purposeful overlaps but all four silhouettes recognizable. Keep the left 45 percent nearly empty, evenly lit off-white, to receive a separate HTML heading; do not place any text in the image. The microphone lies diagonally in front, the camera stands behind it, the spotlight is farthest right, and the closed folio lies flat beneath the rear edge of the camera without becoming a platform for the whole group. Main materials are neutral matte black #000000 ceramic or anodized metal and satin chrome. Add small opaque cobalt-lacquer #2B5FE3 accents only to the microphone collar, camera shutter button and folio tab; blue covers less than 5 percent of the composition. Black stays neutral, never navy. Use a three-quarter camera rotated 30 degrees horizontally and 20 degrees above the tabletop, long-lens perspective, a large soft upper-left light and restrained neutral fill from right. Create fine physically plausible material detail, small manufactured bevels and soft real contact shadows. Do not add people, hands, screens with content, text, letters, numbers, logos, watermark, brand marks, cables, cups, plants, portraits, event photographs, blue glass, translucent blue shapes, water, waves, ribbons, abstract sculpture, confetti, particles, lens flare, neon light or a dark background. Do not bake UI panels, buttons, headlines or decorative frames into the picture.
```

### Приёмка

Все четыре предмета различимы. Левая область пригодна для чёрного заголовка без маски и тени. Нет волн, прозрачного синего стекла и абстрактного декора. После кропа 3:2 или 16:9 главный предметный ряд сохраняется.


## 02. Ведущий и звук

`tandau-microphone.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P1

Один ручной микрофон с матовым чёрным корпусом, металлической сеткой и тонким кобальтовым кольцом.

### Предмет и задача

Сделать предметную систему узнаваемой с первой иконки. Это один из трёх образцов для согласования всей коллекции.

Один ручной микрофон без стойки и провода.

### Композиция и материалы

Длинная диагональ снизу слева вверх направо. Сетка и рукоять целиком входят в кадр. Предмет лежит, а не висит.

Чёрный анодированный корпус, сатинированная металлическая сетка, одно тонкое кольцо непрозрачного кобальтового лака.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Категория ведущих и звукового сопровождения, карточка направления на лендинге. Не использовать как фотографию оборудования исполнителя.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object is one professional handheld microphone. Give it a long slightly tapered matte-black anodized-metal cylindrical handle, a rounded satin-chrome woven-metal grille at the top, a thin opaque cobalt collar directly below the grille, and a small recessed connector at the bottom. The grille must look like fine real metal mesh, not a smooth sphere. Position the microphone diagonally from lower left to upper right, gently resting on the implied plane rather than hovering. Show the handle and grille fully. The handle is blank, without a switch label or model name. Do not add a microphone stand, cable, receiver, stage, sound waves, screen, case, extra microphone or platform. Preserve realistic microphone proportions and make the mesh detail quiet enough to avoid visual noise when reduced. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

На размере 96 px это микрофон, а не фонарик. Сетка не похожа на гладкий шар. Рядом нет второго микрофона, провода или стойки.


## 03. Фотосъёмка

`tandau-camera.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P1

Компактная беззеркальная камера с одним объективом, чёрным корпусом и узким хромированным ободком.

### Предмет и задача

Дать ясную пиктограмму фотосъёмки без чужой техники и узнаваемых торговых марок. Это калибровочный образец коллекции.

Одна беззеркальная камера с одним установленным объективом. Внешних аксессуаров нет.

### Композиция и материалы

Камера стоит; видны передняя и правая боковая плоскости. Объектив направлен к зрителю под общим углом коллекции.

Матовый чёрный металл, слабая фактура рукояти, тонкий хромированный ободок, одна маленькая синяя кнопка. Линза тёмная нейтральная, с белыми отражениями.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Категория фотографов, карточка направления на лендинге и иллюстрация типа услуги.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object is one compact professional mirrorless still-photography camera with a single medium-length lens attached. Use a realistic matte-black anodized-metal camera body with a modest textured black grip, one slightly raised viewfinder housing, a satin-chrome lens rim and one small opaque cobalt shutter button on the top-right shoulder. The lens is dark neutral optical glass with restrained white reflections, not luminous or blue glass. Aim the lens toward the viewer at the shared three-quarter angle so both the front and the right side of the body are visible. Make the camera recognizably a still camera with realistic proportions; it must not resemble a cube, a toy or a cinema rig. Keep the body and lens barrel completely free of lettering and numerals. Do not add a strap, tripod, flash unit, second lens, lens cap, memory card, bag, landscape photo or screen content. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

Читается как фотокамера при размере 96 px. Нет логотипа и маркировки объектива. Корпус отличается от видеокамеры силуэтом и не светится синим.


## 04. Видеосъёмка

`tandau-video-camera.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P1

Компактная кинокамера с верхней ручкой, одним объективом и боковым монитором без изображения.

### Предмет и задача

Развести фото и видео по форме предмета, а не только по подписи.

Одна камера с одним объективом, одной верхней ручкой, двумя короткими рельсами и одним боковым монитором.

### Композиция и материалы

Ручка хорошо отделена от корпуса; короткие рельсы видны снизу. Экран расположен сбоку, остаётся пустым и не перетягивает внимание.

Матовый чёрный металл, хромированные рельсы, одна маленькая кобальтовая ручка настройки. Оптика нейтральная.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Категория видеографов и выбор видеосъёмки в брифе.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object is one compact professional cinema camera. Use a matte-black rectangular camera body, one medium cylindrical lens, one slim rectangular top carrying handle, two short satin-chrome support rails below the body, and one small folded-out side monitor with a completely blank dark screen. Keep the monitor modest and turned slightly inward so the lens and handle define the silhouette. Add exactly one tiny opaque cobalt adjustment knob on the camera body. The lens is dark neutral optical glass with a soft white reflection. The shape must clearly differ from a still-photography camera: the top handle, compact body and short rails are visible. Use believable engineered joins and functional dimensions. Do not add a tripod, operator, microphone attachment, large rig, matte box, cable, battery hanging off the rear, film reel, record symbol, red recording light or any screen image. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

При уменьшении видны отличия от фотокамеры. Монитор не содержит текста, красной точки записи и картинки. Дополнительного съёмочного оборудования нет.


## 05. Сценический свет

`tandau-stage-light.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P1

Один компактный поворотный прожектор в чёрной П-образной раме с хромированными осями.

### Предмет и задача

Обозначить техническое оснащение без иллюстрации конкретной услуги или доступного оборудования.

Один прожектор из базы, П-образной рамы и одной цилиндрической головы; две металлические оси.

### Композиция и материалы

Голова наклонена вверх на 15°. Лицевая линза и зазоры вокруг рамы видны целиком. Прожектор выключен.

Чёрный матовый металл, хромированные оси, небольшая синяя вставка в базе, тёмная нейтральная линза.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Категории сценического оборудования и света, предметная графика сценария мероприятия.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object is one compact event-stage moving-head spotlight. Build it from a low matte-black rectangular base, a matte-black U-shaped mechanical yoke, and one cylindrical black lamp head held between the yoke arms by two satin-chrome pivot joints. Tilt the lamp head upward by approximately 15 degrees so the circular front lens is visible. Add one small opaque cobalt inset on the front edge of the base. The front lens is dark neutral glass with a controlled white reflection and is switched off; no visible light beam. Keep the yoke thin enough to look engineered but clearly visible at small sizes. The silhouette should immediately read as stage lighting, not a surveillance camera or domestic desk lamp. Do not add a stand, truss, clamp, cable, beam cone, colored glow, haze, disco ball, speaker or second light. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

Не похож на камеру наблюдения. Нет светового луча, дыма и цветного ореола. Силуэт рамы сохраняется при размере 96 px.


## 06. Площадка мероприятия

`tandau-venue.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P1

Открытый архитектурный макет зала с прямоугольным основанием и тремя высокими оконными проёмами.

### Предмет и задача

Показать пространство мероприятия без чужих фотографий и выдуманной площадки в каталоге.

Один макет: одно основание, две короткие боковые стены, одна задняя стена с тремя оконными проёмами. Крыши и мебели нет.

### Композиция и материалы

Передняя сторона полностью открыта. Видны глубина пола и высокая задняя стена. Три окна образуют ритм.

Матовая чёрная керамика, тонкий хромированный входной порог, одна маленькая синяя входная метка.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Категория площадок и выбор места проведения; декоративная иллюстрация условия города и пространства.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object group is one small architectural scale model of a contemporary event hall, open at the front and without a roof so its interior is visible. Use one low rectangular matte-black ceramic floor slab, two short matte-black side walls, and one rear wall containing exactly three tall narrow window openings. Leave the openings empty, without glass. Fit a very thin satin-chrome threshold across the open front and a tiny opaque cobalt entrance marker at its right end. The interior is completely empty and well proportioned, with a high-ceiling event-hall character rather than a house. Show the rear wall and enough floor area to make the room legible. The walls have small precise bevels and restrained neutral highlights. Do not add furniture, chairs, plants, chandeliers, people, doors with logos, signage, rooftop objects, stage equipment, skyline or a real identifiable venue. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

Виден зал, а не жилой дом или коробка. Проёмов ровно три. Нет узнаваемого здания, мебели и вывесок.


## 07. Флористика и декор

`tandau-floral-arrangement.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P1

Пять натуральных белых калл в невысокой чёрной керамической вазе с тонким металлическим основанием.

### Предмет и задача

Добавить узнаваемый живой предмет и пластичность без превращения всей коллекции в одинаковые геометрические блоки.

Одна низкая ваза, ровно пять калл, не более двух небольших листьев. Упаковки и дополнительного букета нет.

### Композиция и материалы

Пять цветов располагаются на трёх высотах свободным асимметричным веером. Между бутонами остаётся воздух; ваза ниже стеблей.

Натуральные белые лепестки и тёмно-зелёные стебли, матовая чёрная керамика, тонкий хромированный низ, маленькая синяя связка у горлышка.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Категория флористов и декораторов, блок направлений услуг.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object group is one restrained floral arrangement containing exactly five natural ivory-white calla lilies on thin dark green stems, placed in one low matte-black ceramic cylindrical vase with a very narrow satin-chrome foot. Include one tiny unmarked opaque cobalt tie around the lower part of the stem group, mostly hidden at the vase opening. Use real botanical petal curvature and fine natural surfaces, not ceramic or metal flowers. Arrange the five flower heads at three different heights in a calm asymmetric fan, with generous air between them. Keep the vase simple and visibly lower than the stems. Natural petals and the small amount of dark green stem are the only material-color exceptions to the collection palette. Do not add leaves beyond two small natural leaves, filler flowers, bouquet wrapping, ribbons, bows, hearts, labels, decorative stones, a second vase, table setting or event-room background. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

Цветы выглядят натуральными, не металлическими и не пластиковыми. Лепестки сохраняются на прозрачном фоне без белого ореола. Бутонов ровно пять.


## 08. Дата мероприятия

`tandau-calendar.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P1

Настольный календарь с двумя металлическими креплениями, светлым листом и одной синей выбранной ячейкой.

### Предмет и задача

Показать выбранную дату без выдуманного числа и сведений о свободных днях. Это третий калибровочный образец серии.

Один настольный календарь, один светлый лист, два крепления, одна отмеченная ячейка.

### Композиция и материалы

Небольшой наклон назад; лист широкий. Сетка 7 × 5 без цифр. Один синий квадрат расположен ближе к центру.

Чёрная матовая подставка, бумажный светлый лист, сатинированные металлические крепления, непрозрачная кобальтовая отметка.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Шаг даты в брифе и пояснение календарного условия. Не заменяет доступный интерактивный календарь.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object is one compact freestanding desk calendar. Use a thin matte-black backboard and triangular black support, one warm-white paper face, and exactly two small satin-chrome C-shaped binding loops at the top. On the face show a subtle seven-column, five-row grid made from thin neutral-gray embossed rules, with no numbers, letters or month title. Exactly one cell near the center is an opaque cobalt square inset flush with the paper surface. The calendar tilts backward slightly and keeps a wide rectangular outline. Make the two binding loops and the standing silhouette recognizable even when the grid becomes tiny. Do not add checkmarks, clocks, bells, date numerals, text, extra sheets, torn pages, floating squares or a second calendar. This is a conceptual date-selection object, not a real availability schedule. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

На размере 96 px распознаётся календарь. Нет случайных псевдоцифр. Креплений ровно два и синяя ячейка одна. Не выглядит как стеклянный экран.


## 09. Бюджет

`tandau-budget.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P1

Компактный настольный калькулятор с пустым дисплеем, металлическими клавишами и одной синей клавишей.

### Предмет и задача

Обозначить расчёт бюджета узнаваемым инструментом, не создавая обещаний оплаты или финансовой услуги.

Один калькулятор; один пустой дисплей; двенадцать клавиш в сетке 3 × 4, из них одна синяя.

### Композиция и материалы

Калькулятор лежит под общим углом коллекции. Дисплей и вся сетка кнопок видны. Лицевая плоскость слегка наклонена.

Чёрный матовый корпус, низкие металлические клавиши, тёмный пустой дисплей, синяя нижняя правая клавиша.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Ввод бюджета и пояснение ценового ограничения. Все суммы и слово «от» выводятся живым текстом рядом.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object is one small physical desktop calculator with a matte-black anodized-metal body. Give it one blank dark rectangular display and exactly twelve low satin-chrome keys arranged in a three-column, four-row grid. Replace only the bottom-right key with opaque cobalt lacquer. Every key is completely blank, without numerals or mathematical symbols. The display is off and contains no digits. Use believable calculator proportions, a slightly sloped front and subtle concave key tops; keep the corners gently manufactured rather than inflated. Position it flat on the implied surface, angled so the display and full key grid are visible. Do not add coins, banknotes, currency signs, receipt rolls, bank cards, wallet, charts, rising arrows, hand, cables or extra calculator. This object represents defining an event budget, not paying or investing. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

Клавиш ровно двенадцать. На клавишах и дисплее нет цифр и символов. Не выглядит как платёжный терминал, банковская карта или денежный знак.


## 10. Короткий список

`tandau-shortlist.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P2

Три светлые предметные карточки, собранные одним чёрным зажимом; одна карточка выделена небольшой синей вкладкой.

### Предмет и задача

Показать небольшой набор вариантов. Наличие трёх карточек в символе не гарантирует три результата на любой запрос.

Ровно три плотные карточки и один канцелярский зажим. Одна синяя вкладка у передней карточки.

### Композиция и материалы

Верхние края смещены равномерно, чтобы все три карточки можно было пересчитать. Зажим служит небольшим упором.

Светлый плотный картон, чёрный металлический зажим, хромированные ручки, непрозрачная синяя вкладка.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Сохранённые варианты и вступление к подборке до трёх подрядчиков.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object group is a tidy shortlist made of exactly three thick warm-white physical index cards held together by one small matte-black binder clip with satin-chrome wire handles. The three cards are offset upward by a small even distance so all three separate top edges can be counted. Each card is completely blank. Add one small opaque cobalt rectangular tab to the right edge of the front card. Stand the group at a slight backward lean using the binder clip as a discreet support; do not add a separate pedestal. Keep real paperboard thickness and crisp, softly beveled cut edges, without pill-shaped corners. The clip must look like a real mechanical stationery clip, not an abstract cube. Do not add names, portraits, contact details, lines of fake writing, stars, scores, checkmarks, a fourth card, phone frame or application UI. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

Карточек ровно три. Нет портретов, контактов, рейтинга и имитации текста. Зажим узнаваем, карточки не превращены в экраны смартфонов.


## 11. Сравнение вариантов

`tandau-comparison.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P2

Небольшие точные настольные весы с двумя плоскими чашами и одинаковыми чёрными образцами.

### Предмет и задача

Обозначить внимательное сравнение без назначения победителя одним декоративным знаком.

Одни настольные весы, две чаши и два одинаковых образца. На правом образце одна синяя вставка.

### Композиция и материалы

Перекладина строго горизонтальна; чаши на одной высоте. Образцы равного размера. Цепей нет.

Матовая чёрная база и образцы, тонкие хромированные стойка и перекладина, небольшая непрозрачная синяя метка.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Сопоставление условий двух вариантов и раздел объяснений. Не отображает математический рейтинг или вероятность.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object group is one compact modern tabletop balance used as a metaphor for comparing two options. Use a low matte-black circular base, one slender satin-chrome upright, one level satin-chrome crossbeam and exactly two shallow rectangular chrome weighing trays, one at each end. Place one identical small matte-black sample block on each tray. Add one tiny opaque cobalt square inset on the upper face of the right-hand block only. Both trays are at the same height; the crossbeam is exactly level. Use functional mechanical pivots and clean contemporary proportions, with no chains. The objects should read as a balanced comparison, not a judgment or promise that one provider is better. Do not add a justice figure, legal emblem, coins, numbers, scale marks, gauge, needle, arrows, winner symbol, extra tray or tilted beam. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

Видны две равные стороны. Нет юридического герба, денежных знаков и наклона, который объявлял бы один вариант лучшим.


## 12. Бриф мероприятия

`tandau-brief.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P1

Чёрный планшет с одним светлым листом, металлическим зажимом и синим карандашом справа.

### Предмет и задача

Связать заполнение формы с понятным человеческим действием подготовки задания.

Один планшет, один лист, один верхний зажим и один карандаш.

### Композиция и материалы

Планшет показан почти лежащим. Карандаш справа параллелен длинной стороне, между ними небольшой просвет. На листе три пары тонких линий.

Чёрная матовая основа, светлая бумага, хромированный зажим, непрозрачный кобальтовый карандаш с графитовым концом.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Ввод условий мероприятия, начало сценария подбора, раздел семи фаз продукта.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object group contains one physical matte-black clipboard with one warm-white paper sheet under a satin-chrome top clip, plus one slim opaque cobalt-lacquer pencil placed along its right side. The pencil has a natural graphite tip and no lettering. On the sheet use exactly three groups of shallow neutral-gray horizontal embossed rules; each group contains two lines. These are simple physical rules, not text or symbols. Leave plenty of blank paper around them. The clipboard lies at a shallow backward angle with the clip and paper surface visible. Keep the pencil separate by a narrow clear gap and aligned parallel to the long clipboard edge. Do not add checkboxes, checkmarks, words, dates, numbers, extra sheets, sticky notes, pen cap, hand, phone, tablet device, monitor or other desk props. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

Не выглядит как планшетный компьютер. На бумаге только шесть линий в трёх группах, без символов. Карандаш один и не сливается с краем.


## 13. Шаг выполнен

`tandau-complete.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P2

Одна плоская чёрная объёмная галочка с тонкой металлической гранью и маленькой синей вставкой.

### Предмет и задача

Дать спокойное подтверждение действия без наградных и сертификационных ассоциаций.

Одна объёмная галочка из двух соединённых плоских ветвей. Видимого пьедестала нет.

### Композиция и материалы

Короткая левая и длинная правая ветвь; знак стоит на нижней точке. Небольшая опора скрыта за соединением.

Матовая чёрная керамика, узкая хромированная грань, маленькая синяя вставка на длинной ветви.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Локально завершённый шаг брифа или успешное действие. Не знак проверенного подрядчика и не подтверждённая бронь.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object is one freestanding sculptural checkmark made from matte-black ceramic. Build it from two flat straight arms joined at a precise angle, with a short left arm and a longer rising right arm. Give the front face a consistent modest thickness, small physical bevels and a narrow satin-chrome edge visible along one side. Add one tiny opaque cobalt inset near the end of the longer arm. Rest the lowest point on the implied surface with a discreet physically plausible support hidden behind the lower junction; do not add a visible platform. Keep the checkmark slender, simple and legible. This symbol indicates the completion of a local user step only. Do not enclose it in a square, circle, shield, badge, seal, medal or card, and do not add ribbons, stars, certificates, text, confetti, glow or additional checkmarks. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

Знак считывается при размере 96 px. Вокруг нет круга, щита, карточки или печати. Не похож на надутую пластиковую игрушку.


## 14. Пустой раздел

`tandau-open-folder.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P2

Приоткрытая чёрная папка без документов с небольшим металлическим усилением и синей вкладкой.

### Предмет и задача

Обозначить свободное место без тревоги и ощущения ошибки. Одно изображение не подменяет пять разных текстовых исходов подбора.

Одна открытая папка, внутри нет содержимого.

### Композиция и материалы

Панели раскрыты примерно на 35°. Нижний сгиб служит опорой. Пустой внутренний объём хорошо виден.

Матовый чёрный плотный картон, узкое металлическое усиление сгиба, маленькая синяя внутренняя вкладка.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Пустое избранное, пустая история и отсутствие результатов при корректном запросе. Текст рядом объясняет конкретную ситуацию.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object is one open physical document folder made from rigid matte-black fiberboard with a fine natural paper texture. Give the rear panel one modest offset tab at the upper left and the front panel a slightly lower straight top edge. Open the two panels by approximately 35 degrees so the empty interior is clearly visible. The folder contains no paper or other objects. Add one narrow satin-chrome reinforcement along the lower hinge and one tiny opaque cobalt tab on the inner right edge. Use realistic thin board thickness with small cut-edge bevels; the folder is not a metal safe or a plastic box. Position it standing on its lower fold with both outer and inner surfaces readable. Do not add loose sheets, magnifying glass, question mark, error cross, sad face, lock, warning symbol, broken edge, debris, lettering or UI panel. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

Папка явно пустая. Нет вылетевших листов, замка, грустного лица и символа ошибки. Она не выглядит сейфом или ноутбуком.


## 15. Личный доступ

`tandau-keycard.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P2

Одна чёрная карта доступа в тонком металлическом держателе с маленькой синей вставкой.

### Предмет и задача

Показать личный доступ простым физическим предметом без банковских и биометрических ассоциаций.

Одна карта и один низкий держатель.

### Композиция и материалы

Большая часть карты видна над держателем. Карта чуть наклонена назад, лицевая сторона пустая, толщина различима.

Матовая чёрная карта, сатинированный хромированный держатель, одна маленькая синяя вставка.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Боковая иллюстрация входа и регистрации, вступление к кабинету. Не обозначает оплату и не доказывает сертификацию безопасности.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object group contains one matte-black physical access keycard inserted a short distance into one low satin-chrome card holder. The card is a thin vertical rectangle with real manufactured corner radii, approximately the proportions of a hotel access card, and a very subtle satin surface. It contains one small flush opaque cobalt square near its upper-right corner, with no other marks. The holder is a narrow simple slotted chrome block supporting only the bottom edge; most of the card remains visible. Lean the card backward slightly and show the front face and thickness at the shared camera angle. The card is completely blank: no name, portrait, number, chip, magnetic stripe, contactless symbol or organization logo. Do not add keys, locks, shields, fingerprints, keypad, safe, money, bank-card details, lanyard, hands or multiple cards. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

Нет имени, фото, чипа, банковской маркировки и контактного символа. Держатель не похож на платёжный терминал. Карта только одна.


## 16. Выбор из трёх

`tandau-choice-tray.png` · 1600 × 1600 px · RGBA PNG с прозрачным фоном · P2

Низкий чёрный органайзер с тремя секциями и тремя предметными плитками; средняя плитка выдвинута и отмечена синей полосой.

### Предмет и задача

Передать ограниченный понятный выбор и одно действие организатора. Синяя метка означает внимание пользователя, не автоматическую гарантию лучшего исполнителя.

Один лоток с тремя секциями, два разделителя, ровно три одинаковые плитки.

### Композиция и материалы

Средняя плитка с синей полосой на передней грани сдвинута вперёд на четверть своей длины. Боковые плитки остаются на одном уровне. Передняя стенка лотка низкая.

Матовый чёрный лоток и три чёрные плитки, два тонких хромированных разделителя, одна узкая полоса непрозрачного кобальтового лака на средней плитке.

Камера, освещение и свободное поле соответствуют общей системе. Для hero исключение составляет распределение группы справа и свободного поля слева.

### Размещение

Крупная композиция возле результатов и объяснение короткого списка. Используется отдельно от галереи предметных категорий.

### Полный промпт для генерации

```text
Create an isolated photorealistic 3D product render for the Tandau event-planning interface. Use genuine black #000000 for the main matte surfaces, satin chrome for functional metal parts, and one small opaque cobalt-lacquer accent #2B5FE3 covering less than 8 percent of the visible object. Black must stay neutral, never navy or blue-tinted; realistic gray reflections are allowed. Use precise manufactured edges and small physical bevels, with curves only where the real object requires them. Match this camera across the collection: a three-quarter view rotated 30 degrees horizontally, elevated 20 degrees, with orthographic or long-lens perspective and no wide-angle distortion. Use a large soft key light from upper left and a weaker neutral fill from right. Center the complete object group, leaving at least 14 percent clear padding on every side. Preserve a readable silhouette at 96 pixels. Export 1600 by 1600 pixels as sRGB RGBA PNG with true transparent background and only a very faint translucent contact shadow. The only object group is one low matte-black desktop organizer tray divided into exactly three equal parallel compartments by two thin satin-chrome separators. Place exactly one flat rectangular sample tile in each compartment. All three tiles are matte black with subtle neutral-gray edge highlights. The center tile is shifted forward by approximately one quarter of its length and has one narrow opaque cobalt-lacquer strip across its front edge. All three tiles have the same dimensions and thin manufactured profiles. Keep the front lip of the tray low so the tiles and their offsets remain clearly visible. Add no symbols or markings to the tiles. The tray should resemble a precise physical sorting tool, not an application screenshot or a row of smartphones. Show enough of the top plane to count all three compartments. Do not add a fourth compartment, extra tile, checkmark, portrait, writing, rating, screen frame, arrow, floating item, glass, glowing edge or decorative platform. Do not add text, letters, numbers, logos, watermark, brand marks, UI screenshots, people, hands, decorative waves, blue glass, translucent blue material, navy surfaces, inflated plastic, toy proportions, gummy edges, floating particles, sparkles, lens flare, confetti, heavy shadows, environment, pedestal beyond the specified object, fake checkerboard transparency or a solid rectangular background. Do not crop any part of the object.
```

### Приёмка

Можно пересчитать три секции и три плитки. Они не похожи на смартфоны. Синяя полоса непрозрачная, не стеклянная; нет галочки или звезды.


## Порядок передачи

Сначала передайте три калибровочных файла — микрофон, камеру и календарь. Нужны именно PNG с полными именами из таблицы, без суффиксов `final`, пробелов и изменения регистра. После согласования общих материалов и света подготовьте остальные тринадцать по тем же правилам.

Если генератор не выдаёт настоящий альфа-канал, приложите исходный результат и явно укажите отсутствие прозрачности. Не стирайте края предмета вручную грубой маской и не выдавайте белую подложку за прозрачность. Тонкую сетку микрофона, белые лепестки и металлические петли проверяем особенно внимательно.

Не уменьшайте мастер перед передачей и не применяйте мессенджерное сжатие. Мастера сохраняются в PNG. Облегчённые форматы и размеры под конкретные экраны готовятся отдельно при интеграции.

## Проверка готовой серии

1. Получены 16 файлов с точными именами. Hero имеет размер 2400 × 1600, остальные файлы 1600 × 1600.
2. Чёрный нейтральный. Матовые поверхности не стали тёмно-синими. Хром и маленькие непрозрачные синие детали выдержаны одинаково.
3. Камера, тени и направление бликов согласованы с тремя калибровочными образцами.
4. Количество предметов и деталей соответствует каждому брифу. Особенно проверены пять калл, три окна, три карточки, двенадцать клавиш и три секции лотка.
5. При уменьшении до 96 px категория или действие остаются понятными. На размере 320 px видны чистые грани без артефактов.
6. Прозрачность настоящая, без белой каймы и нарисованной шахматной сетки. Предметы не обрезаны.
7. Нет текста, случайных символов, логотипов, лиц, фотографий подрядчиков, рейтингов и вымышленных данных.
8. Hero содержит ровно четыре предмета и свободное левое поле под живой заголовок. Ни одно изображение не содержит волн или синих стеклянных фигур.
9. Предметы выглядят физически возможными. Камера не похожа на игрушку, флористика не металлическая, чёрные грани читаются без неонового контура.
10. Символы не обещают оплату, подтверждённую бронь, проверенную личность или безусловную безопасность.

## Правила использования в интерфейсе

Предметная графика поддерживает смысл раздела. Она не заменяет подпись, кнопку и информацию о подрядчике. В рабочем результате текст и условия имеют приоритет над иллюстрацией. Не ставить объёмный объект в каждое поле и в каждую строку карточки.

Маленькие элементы управления используют простые векторные пиктограммы. Предметные изображения показываются преимущественно в диапазоне 96–240 px. В категорийной сетке одинаковая область отводится каждой иконке, но отдельные объекты можно оптически выравнивать по массе, сохраняя свободное поле.

Если смысл уже передан соседней подписью, изображение имеет пустой `alt=""`. Если оно несёт самостоятельную информацию, alt коротко описывает предмет без художественных эпитетов и без утверждений о реальном подрядчике. Hero декоративный и имеет пустой alt.

Изображения не загружаются все сразу в полном разрешении. При интеграции задать размеры, подготовить подходящие производные, отложить загрузку нижних секций и сохранить альфа-канал. Пока файлы не получены, дизайнбук показывает только честные карточки запросов с именем, назначением, форматом и полным промптом.

Машиночитаемая версия пакета находится в [`asset-briefs.json`](../app/static/assets/tandau/asset-briefs.json). Она содержит 16 запросов и не является реестром уже сгенерированных изображений.
