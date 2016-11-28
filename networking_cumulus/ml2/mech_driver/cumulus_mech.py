import netaddr
from oslo_config import cfg
from oslo_log import log
from oslo_utils import timeutils

from neutron.common import rpc as n_rpc
from neutron.common import topics
from neutron import context as neutron_context
from neutron.extensions import portbindings
from neutron import manager
from neutron.plugins.common import constants as p_const
from neutron.plugins.ml2 import driver_api as api
from neutron.plugins.ml2.drivers import mech_agent
from neutron_lib import constants as common_const

from networking_cumulus._i18n import _LI, _LE
from networking_cumulus.common import constants
from networking_cumulus.ml2.agent import cumulus_agent_rpc

LOG = log.getLogger(__name__)


class CumulusLBAgentMechanismDriver(mech_agent.SimpleAgentMechanismDriverBase):
    """Attach to networks using linux bridges on Cumulus switch.

    The CumulusLBAgentMechanismDriver integrates the ml2 plugin with the
    Cumulus Agent. Port binding with this driver requires the
    Cumulus Agent to be running on the cumulus switch.
    """
    def __init__(self):
        super(CumulusLBAgentMechanismDriver, self).__init__(
            constants.AGENT_TYPE_CUMULUS,
            portbindings.VIF_TYPE_OTHER,
            {portbindings.CAP_PORT_FILTER: True})
        self.context = neutron_context.get_admin_context()
        self._start_rpc_listeners()
        self._pool = None
        self.supported_vnic_types = [portbindings.VNIC_BAREMETAL]
        self.supported_network_types = [p_const.TYPE_VLAN]
        LOG.info(_LI("Successfully initialized Cumulus Mechanism driver."))

    def get_allowed_network_types(self, agent):
        return (agent['configurations'].get('tunnel_types', []) +
                [p_const.TYPE_VLAN])

    def get_mappings(self, agent):
        return agent['configurations'].get('bridge_mappings', {})

    def _start_rpc_listeners(self):
        self.agent_notifier = cumulus_agent_rpc.CumulusRpcClientAPI(self.context)

    def create_port_postcommit(self, context):
        pass

    def update_port_postcommit(self, context):
        pass

    def delete_port_postcommit(self, context):
        """Delete port non-database commit event."""
#        port = context.current
#        import rpdb
#        debugger = rpdb.Rpdb(port=12345)
#        debugger.set_trace()
#        if port and port['device_owner'].startswith('compute'):
#            segment = context.top_bound_segment
#            if (segment and
#                    segment[api.NETWORK_TYPE] in self.supported_network_types):
#                LOG.debug("Cumulus Mech driver - delete_port_postcommit for "
#                          "port: %s with network_type as %s.",
#                          port['id'], segment[api.NETWORK_TYPE])
#                vni = segment[api.SEGMENTATION_ID]
#                network_type = segment[api.NETWORK_TYPE]
#                host = port[portbindings.HOST_ID]
        pass

    def create_network_postcommit(self, context):
        self.agent_notifier.create_network_cast(current=context.current)

    def delete_network_postcommit(self, context):
        self.agent_notifier.delete_network_cast(current=context.current)
        

    def bind_port(self, context):
        segments = context.network.network_segments
        for segment in segments:
            if segment[api.NETWORK_TYPE] in self.supported_network_types:
                port = context.current
                vnic_type = port[portbindings.VNIC_TYPE]
                if vnic_type in self.supported_vnic_types:
                    self.agent_notifier.bind_port_call(current=context.current)
    
