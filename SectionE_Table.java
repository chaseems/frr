/**
 * 清空 SectionE 类型表格的原始空数据节点。
 *
 * 与 clearTableFirstRow() 的区别：
 *   - clearTableFirstRow() 删除所有直接子节点（适用于 TrusteeTable 等纯数据表格）
 *   - 本方法只删除普通数据节点，保留 xfa:dataNode="dataGroup" 的结构节点
 *     （HeaderRow、RowButtons_sub 等），否则 Adobe 渲染会出错
 *
 * 适用表格：ContributorTable_sub、DistributionTable、IndebtedTable、LenderTable
 *
 * @param tableName 表格容器节点名
 */
public void clearSectionETableRows(String tableName) {
    Element docEle = getDoc().getDocumentElement();
    NodeList nl = docEle.getElementsByTagName(tableName);
    if (nl == null || nl.getLength() == 0) {
        System.out.println("[WARN] 表格未找到: " + tableName);
        return;
    }
    Element table = (Element) nl.item(0);

    String XFA_NS = "http://www.xfa.org/schema/xfa-data/1.0/";

    // 收集要删除的节点：只删非 dataGroup 的普通数据节点
    List<Node> toRemove = new ArrayList<>();
    NodeList children = table.getChildNodes();
    for (int i = 0; i < children.getLength(); i++) {
        Node child = children.item(i);
        if (child.getNodeType() != Node.ELEMENT_NODE) continue;

        Element el = (Element) child;
        String dataNode = el.getAttributeNS(XFA_NS, "dataNode");

        // 跳过 xfa:dataNode="dataGroup" 的结构节点（HeaderRow、RowButtons_sub 等）
        if ("dataGroup".equals(dataNode)) continue;

        toRemove.add(el);
    }

    for (Node n : toRemove) table.removeChild(n);

    System.out.println("[XFA] 已清空 " + tableName
        + " 数据节点（" + toRemove.size() + " 个），保留结构节点");
}
