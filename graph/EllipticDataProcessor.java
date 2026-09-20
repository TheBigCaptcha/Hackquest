import java.io.*;
import java.util.*;



public class EllipticDataProcessor {

    // Simple Data Structures to hold the graph in memory
    static Map<String, String> nodes = new HashMap<>(); // txId -> label (1, 2, or unknown)
    static Map<String, List<String>> outEdges = new HashMap<>(); // Source -> Targets
    static Map<String, List<String>> inEdges = new HashMap<>();  // Target -> Sources

    public static void main(String[] args) throws Exception {
        // Ensure you have these files in the same directory as this Java file
        String classesFile = "elliptic_txs_classes.csv";
        String edgesFile = "elliptic_txs_edgelist.csv";

        System.out.println("--- STARTING GRAPH PROCESSING ---");

        // 1. Build transaction graph from actual data
        loadDataset(classesFile, edgesFile);

        // 2. Implement basic graph metrics/clustering
        findIsolatedClusters();

        // 3. Produce node/edge output
        exportProcessedGraph("output_nodes.csv", "output_edges.csv");

        // 4. Commit working code
        System.out.println("\nProcessing complete! You can now commit your code and output files using Git.");
    }

    /**
     * Requirement 1: Build transaction graph from actual data
     */
    public static void loadDataset(String classesFile, String edgesFile) throws Exception {
        System.out.println("\n1. Loading graph from dataset...");

        // Load Nodes and Classes
        Scanner nodeScanner = new Scanner(new File(classesFile));
        if (nodeScanner.hasNextLine()) nodeScanner.nextLine(); // Skip header
        
        while (nodeScanner.hasNextLine()) {
            String[] parts = nodeScanner.nextLine().split(",");
            if (parts.length >= 2) {
                String txId = parts[0].trim();
                String label = parts[1].trim();
                nodes.put(txId, label);
                outEdges.put(txId, new ArrayList<>());
                inEdges.put(txId, new ArrayList<>());
            }
        }
        nodeScanner.close();

        // Load Edges
        Scanner edgeScanner = new Scanner(new File(edgesFile));
        if (edgeScanner.hasNextLine()) edgeScanner.nextLine(); // Skip header
        
        int edgeCount = 0;
        while (edgeScanner.hasNextLine()) {
            String[] parts = edgeScanner.nextLine().split(",");
            if (parts.length >= 2) {
                String src = parts[0].trim();
                String dst = parts[1].trim();
                
                // Safety check: if an edge contains a node missing from the classes file, add it
                nodes.putIfAbsent(src, "unknown");
                nodes.putIfAbsent(dst, "unknown");
                outEdges.putIfAbsent(src, new ArrayList<>());
                inEdges.putIfAbsent(dst, new ArrayList<>());

                outEdges.get(src).add(dst);
                inEdges.get(dst).add(src);
                edgeCount++;
            }
        }
        edgeScanner.close();

        System.out.println("Loaded " + nodes.size() + " nodes and " + edgeCount + " edges.");
    }

    /**
     * Requirement 2: Implement basic graph metrics/clustering
     * Finds weakly connected components (clusters of interacting wallets) using basic Depth-First Search.
     */
    public static void findIsolatedClusters() {
        System.out.println("\n2. Running clustering algorithm (Finding Weakly Connected Components)...");
        
        Set<String> visited = new HashSet<>();
        int clusterCount = 0;
        int largestClusterSize = 0;

        for (String node : nodes.keySet()) {
            if (!visited.contains(node)) {
                clusterCount++;
                
                // Track how many nodes are in this specific cluster
                Set<String> currentCluster = new HashSet<>();
                dfs(node, visited, currentCluster);
                
                if (currentCluster.size() > largestClusterSize) {
                    largestClusterSize = currentCluster.size();
                }
            }
        }
        System.out.println("Total isolated transaction clusters found: " + clusterCount);
        System.out.println("Largest single cluster contains " + largestClusterSize + " transactions.");
    }

    // Simple Recursive DFS helper for clustering
    private static void dfs(String node, Set<String> globalVisited, Set<String> currentCluster) {
        globalVisited.add(node);
        currentCluster.add(node);

        // Traverse all outputs (funds sent)
        if (outEdges.containsKey(node)) {
            for (String neighbor : outEdges.get(node)) {
                if (!globalVisited.contains(neighbor)) {
                    dfs(neighbor, globalVisited, currentCluster);
                }
            }
        }

        // Traverse all inputs (funds received)
        if (inEdges.containsKey(node)) {
            for (String neighbor : inEdges.get(node)) {
                if (!globalVisited.contains(neighbor)) {
                    dfs(neighbor, globalVisited, currentCluster);
                }
            }
        }
    }

    /**
     * Requirement 3: Produce node/edge output
     */
    public static void exportProcessedGraph(String nodeFile, String edgeFile) throws Exception {
        System.out.println("\n3. Exporting processed graph data...");

        // Export Nodes with metrics
        FileWriter nodeWriter = new FileWriter(nodeFile);
        nodeWriter.write("Id,Label,InDegree,OutDegree\n");
        for (String nodeId : nodes.keySet()) {
            String label = nodes.get(nodeId);
            int inDegree = inEdges.getOrDefault(nodeId, new ArrayList<>()).size();
            int outDegree = outEdges.getOrDefault(nodeId, new ArrayList<>()).size();
            nodeWriter.write(nodeId + "," + label + "," + inDegree + "," + outDegree + "\n");
        }
        nodeWriter.close();

        // Export Edges
        FileWriter edgeWriter = new FileWriter(edgeFile);
        edgeWriter.write("Source,Target\n");
        for (String src : outEdges.keySet()) {
            for (String dst : outEdges.get(src)) {
                edgeWriter.write(src + "," + dst + "\n");
            }
        }
        edgeWriter.close();

        System.out.println("Successfully created '" + nodeFile + "' and '" + edgeFile + "'.");
    }
}