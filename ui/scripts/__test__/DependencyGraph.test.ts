import {DependencyGraph} from "../DependencyGraph.ts";

describe("DependencyGraph", () => {
  let graph: DependencyGraph;

  beforeEach(() => {
    graph = new DependencyGraph();
  });

  describe("empty graph", () => {
    it("should have no vertices", () => {
      expect(graph.getVertices()).toHaveLength(0);
    });

    it("should have no edges", () => {
      expect(graph.getEdges()).toHaveLength(0);
    });
  });

  describe("adding vertices and edges", () => {
    it("should add a single vertex with no dependencies", () => {
      graph.add({className: "A", requires: []});

      expect(graph.getVertices()).toEqual(["A"]);
      expect(graph.getEdges()).toHaveLength(0);
    });

    it("should add vertex with dependencies", () => {
      graph.add({className: "A", requires: ["B", "C"]});

      expect(graph.getVertices()).toContain("A");
      expect(graph.getVertices()).toContain("B");
      expect(graph.getVertices()).toContain("C");
      expect(graph.getEdges()).toEqual([["A", "B"], ["A", "C"]]);
    });

    it("should handle multiple additions", () => {
      graph.add({className: "A", requires: ["B"]});
      graph.add({className: "B", requires: ["C"]});
      graph.add({className: "C", requires: []});

      expect(graph.getVertices()).toEqual(["A", "B", "C"]);
      expect(graph.getEdges()).toEqual([["A", "B"], ["B", "C"]]);
    });
  });

  describe("getting dependencies", () => {
    beforeEach(() => {
      graph.add({className: "A", requires: ["B", "C"]});
      graph.add({className: "B", requires: ["D"]});
      graph.add({className: "C", requires: []});
      graph.add({className: "D", requires: []});
    });

    it("should return correct dependencies for a vertex", () => {
      expect(graph.getDependencies("A")).toEqual(["B", "C"]);
      expect(graph.getDependencies("B")).toEqual(["D"]);
      expect(graph.getDependencies("C")).toEqual([]);
    });

    it("should return empty array for non-existent vertex", () => {
      expect(graph.getDependencies("X")).toEqual([]);
    });
  });

  describe("cycle detection", () => {
    it("should detect no cycles in acyclic graph", () => {
      graph.add({className: "A", requires: ["B"]});
      graph.add({className: "B", requires: ["C"]});
      graph.add({className: "C", requires: []});

      expect(graph.hasCycle()).toBeFalsy();
    });

    it("should detect direct cycle", () => {
      graph.add({className: "A", requires: ["B"]});
      graph.add({className: "B", requires: ["A"]});

      expect(graph.hasCycle()).toBeTruthy();
    });

    it("should detect indirect cycle", () => {
      graph.add({className: "A", requires: ["B"]});
      graph.add({className: "B", requires: ["C"]});
      graph.add({className: "C", requires: ["A"]});

      expect(graph.hasCycle()).toBeTruthy();
    });

    it("should handle self-dependency", () => {
      graph.add({className: "A", requires: ["A"]});

      expect(graph.hasCycle()).toBeTruthy();
    });
  });

  describe("edge cases", () => {
    it("should handle duplicate dependencies", () => {
      graph.add({className: "A", requires: ["B", "B"]});

      expect(graph.getDependencies("A")).toEqual(["B"]);
      expect(graph.getEdges()).toEqual([["A", "B"]]);
    });

    it("should handle multiple additions of same vertex", () => {
      graph.add({className: "A", requires: ["B"]});
      graph.add({className: "A", requires: ["C"]});

      expect(graph.getDependencies("A")).toEqual(["B", "C"]);
    });
  });

  describe("topological sort", () => {
    it("should return correct order for acyclic graph", () => {
      graph.add({className: "A", requires: ["B", "C"]});
      graph.add({className: "B", requires: ["D"]});
      graph.add({className: "C", requires: ["D"]});
      graph.add({className: "D", requires: []});

      const order = graph.topologicalSort();
      expect(order).not.toBeNull();

      if(order){
        expect(order.indexOf("D")).toBeLessThan(order.indexOf("B"));
        expect(order.indexOf("D")).toBeLessThan(order.indexOf("C"));
        expect(order.indexOf("B")).toBeLessThan(order.indexOf("A"));
        expect(order.indexOf("C")).toBeLessThan(order.indexOf("A"));
      }
    });

    it("should return null for cyclic graph", () => {
      graph.add({className: "A", requires: ["B"]});
      graph.add({className: "B", requires: ["C"]});
      graph.add({className: "C", requires: ["A"]});

      expect(graph.topologicalSort()).toBeNull();
    });

    it("should handle empty graph", () => {
      expect(graph.topologicalSort()).toEqual([]);
    });

    it("should handle single vertex", () => {
      graph.add({className: "A", requires: []});
      expect(graph.topologicalSort()).toEqual(["A"]);
    });

    it("should handle linear dependency chain", () => {
      graph.add({className: "A", requires: ["B"]});
      graph.add({className: "B", requires: ["C"]});
      graph.add({className: "C", requires: []});

      expect(graph.topologicalSort()).toEqual(["C", "B", "A"]);
    });
  });

  describe("removing vertices", () => {
    beforeEach(() => {
      graph.add({className: "A", requires: ["B", "C"]});
      graph.add({className: "B", requires: ["D"]});
      graph.add({className: "C", requires: ["D"]});
      graph.add({className: "D", requires: []});
    });

    it("should remove vertex and its edges", () => {
      graph.remove("B");
        
      expect(graph.getVertices()).not.toContain("B");
      expect(graph.getDependencies("A")).not.toContain("B");
      expect(graph.getEdges()).not.toContain(["B", "D"]);
    });

    it("should remove vertex that is a dependency", () => {
      graph.remove("D");
        
      expect(graph.getVertices()).not.toContain("D");
      expect(graph.getDependencies("B")).not.toContain("D");
      expect(graph.getDependencies("C")).not.toContain("D");
    });

    it("should handle removing non-existent vertex", () => {
      const verticesBefore = graph.getVertices().length;
      const edgesBefore = graph.getEdges().length;
        
      graph.remove("X");
        
      expect(graph.getVertices().length).toBe(verticesBefore);
      expect(graph.getEdges().length).toBe(edgesBefore);
    });

    it("should maintain graph integrity after removal", () => {
      graph.remove("B");
        
      const order = graph.topologicalSort();
      expect(order).not.toBeNull();
      if(order){
        expect(order.indexOf("D")).toBeLessThan(order.indexOf("C"));
        expect(order.indexOf("C")).toBeLessThan(order.indexOf("A"));
      }
    });
  });
});
