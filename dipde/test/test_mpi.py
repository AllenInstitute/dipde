# Set up number of threads for fair comparison:
# import json
# from dipde.interfaces.mpi import MPIJob
# import dipde.interfaces.mpi.benchmark as benchmark
# from dipde.interfaces.mpi.synchronizationharness import MPISynchronizationHarness
# from dipde.profiling import time_network
#
#
#
# def test_benchmark_singlepop(verbose=False, scale=4):
#
#     # Smoke test benchmark code, single core:
#     network = benchmark.get_singlepop_benchmark_network(scale)
#     synchronization_harness = MPISynchronizationHarness(network)
#     time_network(network, synchronization_harness=synchronization_harness)
#
#     # Test to ensure consistent values:
#     result_dict_1 = json.loads(MPIJob(np=1,python='python',module_args=['--benchmark=singlepop', '--scale=%s' % scale],module=benchmark.__file__).run())
#     result_dict_2 = json.loads(MPIJob(np=2,python='python',module_args=['--benchmark=singlepop', '--scale=%s' % scale],module=benchmark.__file__).run())
#     result_dict_4 = json.loads(MPIJob(np=4,python='python',module_args=['--benchmark=singlepop', '--scale=%s' % scale],module=benchmark.__file__).run())
#     for key in result_dict_1:
#         if key != 'run_time':
#             assert result_dict_1[key] == result_dict_2[key] == result_dict_4[key]
#
# def test_benchmark_recurrent_singlepop(verbose=False, scale=4):
#
#     # Smoke test benchmark code, single core:
#     network = benchmark.get_recurrent_singlepop_benchmark_network(scale)
#     synchronization_harness = MPISynchronizationHarness(network)
#     time_network(network, synchronization_harness=synchronization_harness)
#
#     # Test to ensure consistent values:
#     result_dict_1 = json.loads(MPIJob(np=1,python='python',module_args=['--benchmark=recurrent_singlepop', '--scale=%s' % scale],module=benchmark.__file__).run())
#     result_dict_2 = json.loads(MPIJob(np=2,python='python',module_args=['--benchmark=recurrent_singlepop', '--scale=%s' % scale],module=benchmark.__file__).run())
#     result_dict_4 = json.loads(MPIJob(np=4,python='python',module_args=['--benchmark=recurrent_singlepop', '--scale=%s' % scale],module=benchmark.__file__).run())
#     for key in result_dict_1:
#         if key != 'run_time':
#             assert result_dict_1[key] == result_dict_2[key] == result_dict_4[key]
#
# if __name__ == "__main__":                              # pragma: no cover
#     test_benchmark_singlepop(verbose=True)              # pragma: no cover
#     test_benchmark_recurrent_singlepop(verbose=True)    # pragma: no cover