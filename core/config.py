import ConfigParser
import json
import random
import core
import collections


class Config():
    ''' Config
    Config is a simple json object that is loaded into core.CONFIG as a dict

    All sections and subsections must be capitalized. All keys must be lower-case.
    No spaces, underscores, or hyphens.
    Be terse but descriptive.
    '''

    def __init__(self):
        self.configparser = ConfigParser.ConfigParser()
        self.configparser.optionxform = str

        self.file = core.CONF_FILE
        self.base_file = u'core/base_config.cfg'

    def new_config(self):
        ''' Copies base_file to config directory.

        Automatically assigns random values to searchtimehr, searchtimemin,
            installupdatehr, installupdatemin, and apikey.

        Returns str 'Config Saved' on success. Throws execption on failure.
        '''

        with open(self.base_file, 'r') as f:
            config = json.load(f)

        config['Search']['searchtimehr'] = random.randint(0, 23)
        config['Search']['searchtimemin'] = random.randint(0, 59)

        config['Server']['installupdatehr'] = random.randint(0, 23)
        config['Server']['installupdatemin'] = random.randint(0, 59)

        config['Search']['popularmovieshour'] = random.randint(0, 23)
        config['Search']['popularmoviesmin'] = random.randint(0, 59)

        apikey = "%06x" % random.randint(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        config['Server']['apikey'] = apikey

        with open(self.file, 'w') as f:
            json.dump(config, f, indent=4, sort_keys=True)
        return u'Config created at {}'.format(self.file)

    def write_dict(self, data):
        ''' Writes a dict to the config file.
        :param data: dict of Section with nested dict of keys and values:

        {'Section': {'key': 'val', 'key2': 'val2'}, 'Section2': {'key': 'val'}}

        MUST contain fully populated sections or data will be lost.

        Only modifies supplied section.

        After updating config file, copies to core.CONFIG via self.stash()

        Does not return.
        '''

        conf = core.CONFIG

        for k, v in data.iteritems():
            conf[k] = v

        with open(self.file, 'w') as f:
            json.dump(conf, f, indent=4, sort_keys=True)
        # After writing, copy it back to core.CONFIG
        self.stash(config=conf)
        return

    def merge_new_options(self):
        ''' Merges new options in base_config with config

        Opens base_config and config, then saves them merged with config taking priority.

        Does not return
        '''

        new_config = {}

        with open(self.base_file, 'r') as f:
            base_config = json.load(f)
        with open(self.file, 'r') as f:
            config = json.load(f)

        if not config['Quality']['Profiles']['Default'].get('Sources', None):
            config = self._convert_profs(config)

        new_config = self._merge(base_config, config)

        with open(self.file, 'w') as f:
            json.dump(new_config, f, indent=4, sort_keys=True)

        return

    def _merge(self, d, u):
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = self._merge(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    def stash(self, config=None):
        ''' Stores entire config as dict to core.CONFIG
        config: dict config file contents <optional>

        If 'config' is not supplied, reads config from disk. If calling stash() from
            a method in this class pass the saved config so we don't have to read from
            a file we just wrote to.

        Sanitizes input when neccesary

        Does not return
        '''

        if not config:
            with open(self.file, 'r') as f:
                config = json.load(f)

        repl = config['Postprocessing']['replaceillegal']
        if repl in ['"', '*', '?', '<', '>', '|', ':']:
            config['Postprocessing']['replaceillegal'] = ''

        core.CONFIG = config

        return

    def _convert_profs(self, config):
        ''' converts old quality profiles to source-based priority
        config: dict of config file

        Returns dict of converted config file
        '''
        with open(self.base_file, 'r') as f:
            base_new_prof = json.load(f)['Quality']['Profiles']['Default']

        profiles = config['Quality'].pop('Profiles')

        new_profiles = {}

        for k, v in profiles.iteritems():
            new_profiles[k] = json.loads(json.dumps(base_new_prof))
            fourk = v['4K'][0] is True
            new_profiles[k]['Sources']['BluRay-4K'][0] = fourk
            new_profiles[k]['Sources']['WebDL-4K'][0] = fourk
            new_profiles[k]['Sources']['WebRip-4K'][0] = fourk

            teneight = v['1080P'][0] is True
            new_profiles[k]['Sources']['BluRay-1080P'][0] = teneight
            new_profiles[k]['Sources']['WebDL-1080P'][0] = teneight
            new_profiles[k]['Sources']['WebRip-1080P'][0] = teneight
            seventwo = v['720P'][0] is True
            new_profiles[k]['Sources']['BluRay-720P'][0] = seventwo
            new_profiles[k]['Sources']['WebDL-720P'][0] = seventwo
            new_profiles[k]['Sources']['WebRip-720P'][0] = seventwo
            sd = v['SD'][0] is True
            new_profiles[k]['Sources']['DVD-SD'][0] = sd

            new_profiles[k]['ignoredwords'] = v['ignoredwords']
            new_profiles[k]['requiredwords'] = v['requiredwords']
            new_profiles[k]['preferredwords'] = v['preferredwords']
            new_profiles[k]['scoretitle'] = v['scoretitle']
            new_profiles[k]['prefersmaller'] = v['prefersmaller']

        config['Quality']['Profiles'] = new_profiles
        return config
