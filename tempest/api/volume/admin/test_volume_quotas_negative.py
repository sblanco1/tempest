# Copyright 2014 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest.api.volume import base
from tempest import config
from tempest.lib import decorators
from tempest.lib import exceptions as lib_exc

CONF = config.CONF


class BaseVolumeQuotasNegativeTestJSON(base.BaseVolumeAdminTest):
    force_tenant_isolation = True

    @classmethod
    def setup_credentials(cls):
        super(BaseVolumeQuotasNegativeTestJSON, cls).setup_credentials()
        cls.demo_tenant_id = cls.os_primary.credentials.tenant_id

    @classmethod
    def resource_setup(cls):
        super(BaseVolumeQuotasNegativeTestJSON, cls).resource_setup()
        cls.shared_quota_set = {'gigabytes': 2 * CONF.volume.volume_size,
                                'volumes': 1}

        # NOTE(gfidente): no need to restore original quota set
        # after the tests as they only work with dynamic credentials.
        cls.admin_quotas_client.update_quota_set(
            cls.demo_tenant_id,
            **cls.shared_quota_set)

        # NOTE(gfidente): no need to delete in tearDown as
        # they are created using utility wrapper methods.
        cls.volume = cls.create_volume()

    @decorators.attr(type='negative')
    @decorators.idempotent_id('bf544854-d62a-47f2-a681-90f7a47d86b6')
    def test_quota_volumes(self):
        self.assertRaises(lib_exc.OverLimit,
                          self.volumes_client.create_volume,
                          size=CONF.volume.volume_size)

    @decorators.attr(type='negative')
    @decorators.idempotent_id('2dc27eee-8659-4298-b900-169d71a91374')
    def test_quota_volume_gigabytes(self):
        # NOTE(gfidente): quota set needs to be changed for this test
        # or we may be limited by the volumes or snaps quota number, not by
        # actual gigs usage; next line ensures shared set is restored.
        self.addCleanup(self.admin_quotas_client.update_quota_set,
                        self.demo_tenant_id,
                        **self.shared_quota_set)
        new_quota_set = {'gigabytes': CONF.volume.volume_size,
                         'volumes': 2, 'snapshots': 1}
        self.admin_quotas_client.update_quota_set(
            self.demo_tenant_id,
            **new_quota_set)
        self.assertRaises(lib_exc.OverLimit,
                          self.volumes_client.create_volume,
                          size=CONF.volume.volume_size)
