from backend.llmagent.privatestore import ConfluenceStore, BaseStore, BaseConf
from backend.llmagent.conf import class_digestor


def test_class_digestor():
    assert class_digestor.is_subclass_of_base(ConfluenceStore, BaseStore) == True
    print(
        f"ConfluenceStore init params: {class_digestor.get_init_params(ConfluenceStore)}"
    )
    print(f"BaseConf init params: {class_digestor.get_init_params(BaseConf)}")
