import json
import os

import pytest
import yaml
from pytest_mock import MockFixture

from opta.constants import tf_modules_path
from opta.core.generator import gen_all
from opta.exceptions import UserErrors
from opta.layer import Layer
from tests.fixtures.basic_apply import BASIC_APPLY


class TestGenerator:
    def test_gen(self, mocker: MockFixture) -> None:
        mocker.patch("opta.layer.os.path.exists")
        mocker.patch("opta.layer.validate_yaml")

        test_gen_file_path = "pytest_main.tf.json"
        mocker.patch("opta.core.generator.TF_FILE_PATH", test_gen_file_path)

        # Opta configs and terraform files are 1-1 mappings.
        # Make sure the expected terraform file contents are generated
        # from the opta config
        opta_config, gen_tf_file = BASIC_APPLY
        mocked_file = mocker.mock_open(read_data=yaml.dump(opta_config))
        mocker.patch("opta.layer.open", mocked_file)
        opta_config = opta_config.copy()
        mocker.patch("opta.layer.yaml.load", return_value=opta_config)
        layer = Layer.load_from_yaml("", None)
        mocked_state_storage = mocker.patch("opta.layer.Layer.state_storage")
        mocked_state_storage.return_value = "opta-tf-state-test-dev1-98f2"
        gen_all(layer)
        with open(test_gen_file_path) as f:
            real_output = json.load(f)
        assert gen_tf_file == real_output

        # Make sure generation does not work without org name.

        opta_config, _ = BASIC_APPLY
        opta_config = opta_config.copy()
        del opta_config["org_name"]
        mocker.patch("opta.layer.yaml.load", return_value=opta_config)
        with pytest.raises(UserErrors):
            Layer.load_from_yaml("", None)

        os.remove(test_gen_file_path)
