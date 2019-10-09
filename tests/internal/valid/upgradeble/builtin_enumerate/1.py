for i in range(len(counts)):
    support.run_doctest(test_genexps, verbose)
    gc.collect()
    counts[i] = sys.gettotalrefcount()
