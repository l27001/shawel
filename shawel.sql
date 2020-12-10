-- Дамп структуры базы данных Shawel Bot.
-- Дата: 09.12.2020

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `shawel`
--

-- --------------------------------------------------------

--
-- Структура таблицы `chat-rasp`
--

CREATE TABLE `chat-rasp` (
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `mute`
--

CREATE TABLE `mute` (
  `chatid` int(11) NOT NULL,
  `vkid` int(11) NOT NULL,
  `date` int(11) NOT NULL,
  `warn` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `users`
--

CREATE TABLE `users` (
  `vkid` int(30) NOT NULL,
  `dostup` int(11) NOT NULL DEFAULT 0,
  `EXP` int(11) NOT NULL DEFAULT 0,
  `raspisanie` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `vk`
--

CREATE TABLE `vk` (
  `rasp` varchar(500) NOT NULL,
  `vlaga` int(11) DEFAULT NULL,
  `time-poliv` int(11) DEFAULT NULL,
  `autopoliv` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Дамп данных таблицы `vk`
--

INSERT INTO `vk` (`rasp`, `vlaga`, `time-poliv`, `autopoliv`) VALUES
('', 0, 1, 1);

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `chat-rasp`
--
ALTER TABLE `chat-rasp`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `mute`
--
ALTER TABLE `mute`
  ADD KEY `chatid` (`chatid`),
  ADD KEY `vkid` (`vkid`);

--
-- Индексы таблицы `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`vkid`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
