<?php
/*
 * Turbonator Tuning Wiki - local settings
 *
 * Carried over from the 2015 BoostButton wiki (DokuWiki 2014-09-29b "Hrun")
 * when the wiki was moved to the current DokuWiki release.
 * Removed: BoostButton's Google Analytics ID and e-mail addresses,
 * settings of templates and plugins that are no longer installed.
 */

$conf['title'] = 'Turbonator Tuning Wiki';
$conf['tagline'] = 'Archive of the BoostButton Turbonator wiki';
$conf['template'] = 'starterbootstrap';
$conf['sidebar'] = 'navigation';
$conf['license'] = '';
$conf['breadcrumbs'] = 5;
$conf['tocminheads'] = '2';
$conf['useheading'] = 'content';
$conf['useacl'] = 1;
$conf['autopasswd'] = 0;   // users choose their password at registration (no mail needed)
$conf['superuser'] = '@admin';
$conf['target']['interwiki'] = '_blank';
$conf['target']['extern'] = '_blank';
$conf['target']['media'] = '_blank';
$conf['target']['windows'] = '_blank';
$conf['subscribers'] = 1;
$conf['registernotify'] = '';
$conf['mailfrom'] = '';
$conf['sitemap'] = 5;
$conf['updatecheck'] = 0;
$conf['send404'] = 1;
$conf['plugin']['captcha']['mode'] = 'question';
$conf['plugin']['captcha']['question'] = 'Who made both the best chili, and the fastest Chrysler turbo cars?';
$conf['plugin']['captcha']['answer'] = 'Shelby';
// The starterbootstrap template (2015) still uses tpl_action(), which current
// DokuWiki marks as deprecated; keep those notices out of data/log.
$conf['dontlog'] = 'debug,deprecated';
$conf['tpl']['starterbootstrap']['hideTools'] = 1;
$conf['tpl']['starterbootstrap']['full_width'] = 1;
