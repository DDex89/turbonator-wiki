<?php
/**
 * DokuWiki Plugin HowHard (Syntax Component)
 *
 * Shows a "difficulty" badge: {{howhard>1}} ... {{howhard>5}}
 *
 * Original plugin (2012) by Fabrice DEJAIGHER; ported to the current
 * DokuWiki plugin API (PHP 8) for the Turbonator Tuning Wiki archive.
 *
 * @license GPL 2 http://www.gnu.org/licenses/gpl-2.0.html
 * @author  Fabrice DEJAIGHER <fabrice@chtiland.com>
 */

use dokuwiki\Extension\SyntaxPlugin;

class syntax_plugin_howhard extends SyntaxPlugin
{
    private const LEVELS = ['1', '2', '3', '4', '5'];
    private const DEFAULT_LEVEL = '1';

    public function getType()
    {
        return 'substition';
    }

    public function getPType()
    {
        return 'block';
    }

    public function getSort()
    {
        return 195;
    }

    public function connectTo($mode)
    {
        $this->Lexer->addSpecialPattern('\{\{howhard>.*?\}\}', $mode, 'plugin_howhard');
    }

    public function handle($match, $state, $pos, Doku_Handler $handler)
    {
        $level = trim(substr($match, 10, -2));
        if (!in_array($level, self::LEVELS, true)) {
            $level = self::DEFAULT_LEVEL;
        }
        return [$level];
    }

    public function render($format, Doku_Renderer $renderer, $data)
    {
        if ($format !== 'xhtml') {
            return false;
        }
        [$level] = $data;
        $style = $this->getConf('confhowhardstyle') === '2' ? '2' : '1';
        $text = hsc($this->getLang('level' . $level));
        $src = DOKU_BASE . 'lib/plugins/howhard/images/style' . $style . '/' . $level . '.png';

        $renderer->doc .= '<div class="howhard">'
            . '<div class="howhard_title">' . hsc($this->getLang('howhardtitle')) . '</div>'
            . '<div class="howhard_img"><img src="' . $src . '" alt="' . $text . '" /></div>'
            . '<div class="howhard_txt">' . $text . '</div>'
            . '</div>';
        return true;
    }
}
