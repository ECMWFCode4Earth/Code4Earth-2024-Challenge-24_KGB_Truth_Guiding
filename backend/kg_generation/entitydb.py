from typing import TypedDict


class Entity(TypedDict):
    name: str
    label: str
    properties: dict


class EntityDB:
    def __init__(self) -> None:
        self.db: dict[str, dict] = {}
        self.label_set: set[str] = set()

    def add(self, node: Entity):
        if node["name"] not in self.db:
            self.db[node["name"]] = {
                "label": node["label"],
                "properties": node["properties"],
            }
            self.label_set.add(node["label"])
        else:
            pre_node = self.db[node["name"]]
            pre_label, label = pre_node["label"], node["label"]
            pre_node["properties"] |= node["properties"]
            nname = node["name"]
            if pre_label != label:
                print(
                    f"This node {nname} existed with a different label. "
                    f"Old: {pre_label} vs. New: {label}. "
                    "Keep old label."
                )

    def get_node_list(self):
        nodelist = [{"name": k} | v for k, v in self.db.items()]
        return nodelist

    def get_label_set_as_str(self):
        return ", ".join([str(i) for i in self.label_set])
