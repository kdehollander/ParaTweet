      stack =[]
      for b in vocab:
         if b.split()[0] == "start":
            stack.append((b.split()[1], [b.split()[1]]))
      while stack:
         (vertex, path) = stack.pop()
         for next in vocab[vocab.index(vertex)] - set(vocab.index(path)):
            print(next)
            if next == "end":
               yield path + [next]
            else:
               stack.append((next, path + [next]))
