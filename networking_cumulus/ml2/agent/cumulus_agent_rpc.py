import time

from oslo_log import log
import oslo_messaging
from sqlalchemy.orm import exc as sa_exc

from networking_cumulus._i18n import _LE, _LI, _LW
from networking_cumulus.common import constants as c_const

from neutron.common import rpc as n_rpc
from neutron.common import topics
from neutron.db import models_v2
from neutron.db import securitygroups_rpc_base as sg_rpc_base
from neutron.extensions import portbindings
from neutron import manager
from neutron.plugins.common import constants as p_const
from neutron.plugins.ml2 import db
from neutron.plugins.ml2 import driver_api as api
from neutron.plugins.ml2 import driver_context
from neutron.plugins.ml2 import managers
from neutron.plugins.ml2 import rpc as plugin_rpc
from neutron_lib import constants as common_const

LOG = log.getLogger(__name__)

class CumulusAgentRpcCallbacks(object):

    target = oslo_messaging.Target(version='1.2')

    def create_network(self, context, current):
        import pdb; pdb.set_trace()
        LOG.info("FIND ME: create network RPC")

    def create_network(self, context, current):
        import pdb; pdb.set_trace()
        LOG.info("FIND ME: delete network RPC")

    def update_network(self, context, current, segment, original):
        self.update_network_precommit(current, segment, original)

    def bind_port(self, context, current, network_segments, network_current):
        LOG.info("FIND ME: bind port RPC")

    def post_update_port(self, context, current, original, segment):
        self.update_port_postcommit(current, original, segment)

    def delete_port(self, context, current, original, segment):
        self.delete_port_postcommit(current, original, segment)

class CumulusRpcClientAPI(object):

    """Agent side of the Cumulusrpc API."""
    ver = '1.2'

    def __init__(self, context):
        target = oslo_messaging.Target(topic=c_const.CUMULUS, version=self.ver)
        self.client = n_rpc.get_client(target)
        self.context = context

    def _get_device_topic(self, host=None):
        return topics.get_topic_name(topics.AGENT,
                                     c_const.CUMULUS,
                                     topics.UPDATE, host)

    def _get_cctxt(self, host=None):
        return self.client.prepare(
            version=self.ver, topic=self._get_device_topic(host=host))

    def create_network_cast(self, current, host):
        return self._get_cctxt(host).cast(self.context, 'create_network',
                                      current=current)


    def delete_network_cast(self, current, host):
        return self._get_cctxt(host).cast(self.context, 'delete_network',
                                      current=current)

    def bind_port_cast(self, current, host):
        return self._get_cctxt(host).cast(
            self.context, 'bind_port_call', current=current)
