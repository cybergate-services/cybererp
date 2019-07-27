import json
from agent import AsteriskAgent, loop, logger, manager


class CustomAgent(AsteriskAgent):

    def __init__(self, *args, **kwargs):
        super(CustomAgent, self).__init__(args, kwargs)
        manager.register_event('FullyBooted', self.on_asterisk_FyllyBooted)


    async def on_asterisk_FyllyBooted(self, manager, event):
        logger.debug('Asterisk custom event FullyBooted: {}'.format(json.dumps(
                                            dict(event.items()), indent=2)))


if __name__ == '__main__':
    agent = CustomAgent(loop=loop)
    loop.create_task(agent.start())
    try:
        loop.run_forever()
    finally:
        logger.info('Stopped')


