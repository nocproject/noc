export class DependencyGraph{
  private adjacencyList: Map<string, Set<string>> = new Map();

  constructor(){
  }

  add({className, requires}: {className: string, requires: string[] }): void{
    if(!this.adjacencyList.has(className)){
      this.adjacencyList.set(className, new Set());
    }

    for(const require of requires){
      if(!this.adjacencyList.has(require)){
        this.adjacencyList.set(require, new Set());
      }
        this.adjacencyList.get(className)!.add(require);
    }
  }

  remove(classNamePrefix: string): void{
    const classesToRemove = Array.from(this.adjacencyList.keys())
          .filter(className => className.startsWith(classNamePrefix));
      
    for(const className of classesToRemove){
      this.adjacencyList.delete(className);
    }
      
    for(const [, dependencies] of this.adjacencyList){
      for(const className of classesToRemove){
        dependencies.delete(className);
      }
    }
  }
  
  getVertices(): string[]{
    return Array.from(this.adjacencyList.keys());
  }

  getEdges(): Array<[string, string]>{
    const edges: Array<[string, string]> = [];
    for(const [vertex, dependencies] of this.adjacencyList){
      for(const dependency of dependencies){
        edges.push([vertex, dependency]);
      }
    }
    return edges;
  }

  getDependencies(className: string): string[]{
    return Array.from(this.adjacencyList.get(className) || []);
  }

  hasCycle(): boolean{
    const visited = new Set<string>();
    const recStack = new Set<string>();

    const dfs = (vertex: string): boolean => {
      visited.add(vertex);
      recStack.add(vertex);

      for(const neighbor of this.adjacencyList.get(vertex) || []){
        if(!visited.has(neighbor)){
          if(dfs(neighbor)) return true;
        } else if(recStack.has(neighbor)){
          return true;
        }
      }

      recStack.delete(vertex);
      return false;
    };

    for(const vertex of this.adjacencyList.keys()){
      if(!visited.has(vertex)){
        if(dfs(vertex)) return true;
      }
    }

    return false;
  }

  topologicalSort(): string[] | null{
    if(this.hasCycle()){
      return null;
    }

    const graph = new Map(
      Array.from(this.adjacencyList).map(([key, set]) =>
        [key, new Set(set)],
      ),
    );

    const inDegree = new Map<string, number>();
    for(const vertex of graph.keys()){
      inDegree.set(vertex, 0);
    }
    for(const dependencies of graph.values()){
      for(const dep of dependencies){
        inDegree.set(dep, (inDegree.get(dep) || 0) + 1);
      }
    }

    const queue: string[] = [];
    for(const [vertex, degree] of inDegree){
      if(degree === 0){
        queue.push(vertex);
      }
    }

    const result: string[] = [];

    while(queue.length > 0){
      const vertex = queue.shift()!;
      result.unshift(vertex);

      const dependencies = graph.get(vertex) || new Set();
      for(const dependency of dependencies){
        const newDegree = inDegree.get(dependency)! - 1;
        inDegree.set(dependency, newDegree);

        if(newDegree === 0){
          queue.push(dependency);
        }
      }
    }

    return result;
  }
}
