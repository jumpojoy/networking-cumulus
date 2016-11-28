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

from neutron.extensions import providernet as pnet

from networking_cumulus.netconf import netconf

LOG = log.getLogger(__name__)

class CumulusAgentRpcCallbacks(object):

    target = oslo_messaging.Target(version='1.2')

    def create_network(self, context, current):
        segmentation_id = current[pnet.SEGMENTATION_ID]
        with netconf.ConfFile(netconf.INT_BRIDGE) as cfg:
            cfg.ensure_opt_contain_value('bridge-vids', str(segmentation_id))
        LOG.info("FIND ME: create network RPC")

    def delete_network(self, context, current):
        segmentation_id = current[pnet.SEGMENTATION_ID]
        with netconf.ConfFile(netconf.INT_BRIDGE) as cfg:
            cfg.ensure_opt_not_contain_value('bridge-vids', str(segmentation_id))
        LOG.info("FIND ME: delete network RPC")

    def bind_port(self, context, current, network_segments, network_current):
        LOG.info("FIND ME: bind port RPC")


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

    def bind_port_call(self, current, host):
        return self._get_cctxt(host).call(
            self.context, 'bind_port_call', current=current)
