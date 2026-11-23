# Turbonator Wiki — Modernized BoostButton Tuning Wiki

**An archival restoration of the BoostButton / Turbonator tuning wiki**, updated for modern hosting and preserved as a self-contained static website.

The project retains the original community's technical information and adds new documentation for the **Chrysler FCC (1995 Neon)** and **SBEC3 (1996+ Neon / related applications)** engine controllers, based on ongoing firmware reverse-engineering work.

**Language:** English documentation first; a Russian overview is available [below](#на-русском).

## What is included

| Path | Purpose |
| --- | --- |
| `wiki/` | Full DokuWiki site for PHP hosting: editing, search, login, and revision history |
| `static/` | Read-only HTML mirror; works on static hosting and offline in a browser |
| `tools/export_static.py` | Rebuilds the static mirror from the DokuWiki source |
| `.github/workflows/pages.yml` | GitHub Pages deployment workflow |
| `publish-to-github.ps1` | Optional Windows helper for initial Git publication |

The original archive used **DokuWiki 2014-09-29b “Hrun”**. The live version has been migrated to **DokuWiki 2026-07-14c “Mort” (PHP 8.2+)**. Original pages, media, and revision history are preserved; the historical user database was **not** transferred.

The `starterbootstrap` template was adapted for newer PHP. The `wrap` and `captcha` plugins were updated, and the `howhard` plugin was ported to the modern DokuWiki API. Obsolete BoostButton analytics and contact links were removed.

## FCC and SBEC3 firmware documentation

The wiki includes nine additional reference pages based on these open-source projects:

- **[neon-fcc-firmware](https://github.com/DDex89/neon-fcc-firmware)** — 1995 Neon FCC (68HC11): architecture, calibration variants, SCI/DRB communication, fault codes, and tuning notes.
- **[neon-sbec3-firmware](https://github.com/DDex89/neon-sbec3-firmware)** — SBEC3 (68HC16): memory layout, calibration formats, tuning resources, and reflashing background.

The original **FCCFlash** flashing instructions have also been added to the wiki's `flash_an_fcc` page, with references to the existing USB-to-SCI cable setup documentation (`cable_setup` and `manual_ftdi_setup`).

The firmware repositories remain the primary source for detailed, evolving data such as generated address tables, RAM maps, and disassembly annotations. Wiki content is not automatically synchronized with them.

## Running the live wiki

A server with **PHP 8.2+** is required. No database server is needed.

1. Upload the *contents* of `wiki/` to your website directory.
2. Grant the web server write access to `data/` and `conf/`.
3. **Protect sensitive directories from HTTP access.** With Apache, activate the supplied `.htaccess.dist` where appropriate; with nginx, add equivalent access restrictions. Verify that `/data/pages/start.txt` returns HTTP 403 or 404.
4. Create your own administrator account. Do not reuse historical accounts.
5. Review registration and editing permissions before making the site public.

The original wiki's landing-page text may still refer to the now-defunct BoostButton store; update it in the live wiki if appropriate.

For more information on server setup, consult the official [DokuWiki installation documentation](https://www.dokuwiki.org/install).

## Static website and GitHub Pages

The `static/` directory contains an HTML mirror, including assets and local search. Open `static/index.html` to browse it offline, or publish the contents of `static/` on any static web host.

For this repository, the included GitHub Actions workflow can publish the static website using **Settings → Pages → Build and deployment → GitHub Actions**. GitHub Pages does **not** run PHP or support editing the live wiki.

### Rebuild the static copy

Requires Python 3.8+, PHP 8.2+, and Beautiful Soup:

```bash
python -m pip install beautifulsoup4
python tools/export_static.py --wiki wiki --out static
```

The exporter works from a temporary copy of the wiki. After making changes to the live wiki, copy the updated `data/` directory back to `wiki/data/` before regenerating the mirror.

## Contributing

Corrections, missing technical information, restored historical material, and new FCC/SBEC3 pages are welcome. DokuWiki page sources are stored under `wiki/data/pages/`, with images and other media in `wiki/data/media/`.

This is an **archival community project**. Original material remains attributed to its respective authors; modernization and new contributions should not be mistaken for original authorship of the archived content. No license was specified in the original wiki configuration.

---

## На русском

**Turbonator Wiki** — восстановленная и обновлённая техническая вики бывшего сообщества BoostButton. Она посвящена настройке и диагностике автомобилей Chrysler/Dodge/Plymouth, прежде всего Dodge/Plymouth Neon.

Проект состоит из двух версий:

- `wiki/` — полноценная DokuWiki для сервера с PHP 8.2+, с поиском, редактированием и историей изменений.
- `static/` — статическая HTML-копия, работающая без PHP, в том числе локально на компьютере и через GitHub Pages.

Оригинальные страницы, изображения и история правок сохранены. Устаревшие компоненты адаптированы для современных серверов; старые учётные записи пользователей не переносились.

### Новые материалы по ЭБУ

Добавлены разделы по **FCC (1995 Neon, 68HC11)** и **SBEC3 (1996+ Neon, 68HC16)**: архитектура прошивок, калибровки, диагностика, настройка и перепрошивка. Основа этих разделов — репозитории [neon-fcc-firmware](https://github.com/DDex89/neon-fcc-firmware) и [neon-sbec3-firmware](https://github.com/DDex89/neon-sbec3-firmware).

В частности, страница `flash_an_fcc` дополнена инструкцией по FCCFlash и ссылками на настройку кабеля USB-to-SCI.

### Развёртывание

Для живой вики нужен сервер с PHP 8.2+; отдельная база данных не требуется. Для статической копии достаточно открыть `static/index.html` или опубликовать папку `static/` на хостинге. Динамическая версия требует защиты каталогов `data/` и `conf/` от доступа по HTTP.

Английские разделы выше содержат полную инструкцию по установке, экспорту статической копии и GitHub Pages. Исправления и дополнения приветствуются.

**Репозиторий:** https://github.com/DDex89/turbonator-wiki
