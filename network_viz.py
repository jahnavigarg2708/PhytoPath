from pyvis.network import Network

def build_network(overlap_df):
    net = Network(height="600px", width="100%", bgcolor="#0e1117", font_color="white")
    added_nodes = set()

    for _, row in overlap_df.iterrows():
        compound = row["compound_name"]
        gene = row["common_name"]
        try:
            prob = float(row["probability"])
        except (ValueError, TypeError):
            prob = 0.5

        if compound not in added_nodes:
            net.add_node(compound, label=compound, color="#4CAF50", shape="dot", size=20)
            added_nodes.add(compound)

        if gene not in added_nodes:
            net.add_node(gene, label=gene, color="#FF5722", shape="diamond", size=15)
            added_nodes.add(gene)

        net.add_edge(compound, gene, value=prob, title=f"probability: {prob:.2f}")

    net.repulsion(node_distance=150)
    return net