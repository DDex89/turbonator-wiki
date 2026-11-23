<?php
/**
 * Composant Action pour HowHard (Toolbar)
 *
 * @license    GPL 2 (http://www.gnu.org/licenses/gpl.html)
 * @author     Fabrice DEJAIGHER <fabrice@chtiland.com>
 */

use dokuwiki\Extension\ActionPlugin;
use dokuwiki\Extension\EventHandler;
use dokuwiki\Extension\Event;

class action_plugin_howhard extends ActionPlugin
{


	public function register(EventHandler $controller)
	{
		$controller->register_hook('TOOLBAR_DEFINE', 'AFTER', $this, 'handle_toolbar', array ());
	}

	public function handle_toolbar(Event $event, $param)
	{
		$event->data[] = array
		(
			'type'  => 'picker',
			'title' => 'HowHard',
			'icon'  => '../../plugins/howhard/images/toolbar/level_select.png',
			'list'  => array (
				array (
					'type'   => 'insert',
					'title'  => $this->getLang('level1'),
					'icon'   => '../../plugins/howhard/images/toolbar/1.png',
					'insert' => '{{howhard>1}}',
				),
				array (
					'type'   => 'insert',
					'title'  => $this->getLang('level2'),
					'icon'   => '../../plugins/howhard/images/toolbar/2.png',
					'insert' => '{{howhard>2}}',
				),
				array (
					'type'   => 'insert',
					'title'  => $this->getLang('level3'),
					'icon'   => '../../plugins/howhard/images/toolbar/3.png',
					'insert' => '{{howhard>3}}',
				),
				array (
					'type'   => 'insert',
					'title'  => $this->getLang('level4'),
					'icon'   => '../../plugins/howhard/images/toolbar/4.png',
					'insert' => '{{howhard>4}}',
				),
				array (
					'type'   => 'insert',
					'title'  => $this->getLang('level5'),
					'icon'   => '../../plugins/howhard/images/toolbar/5.png',
					'insert' => '{{howhard>5}}',
				)

			)
		);
	}
}

