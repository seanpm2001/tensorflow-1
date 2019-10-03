#!/usr/bin/pypy3
# FakeBazel
# Copyright (C) 2019 Mo Zhou <lumin@debian.org>
import os, sys, re, argparse, shlex, json
from ninja_syntax import Writer
from typing import *

DEBUG=os.getenv('DEBUG', False)

objs_gen_proto_text_functions = '''
external/com_google_absl/absl/base/base/cycleclock.o
external/com_google_absl/absl/base/base/log_severity.o
external/com_google_absl/absl/base/base/raw_logging.o
external/com_google_absl/absl/base/base/spinlock.o
external/com_google_absl/absl/base/base/sysinfo.o
external/com_google_absl/absl/base/base/thread_identity.o
external/com_google_absl/absl/base/base/unscaledcycleclock.o
external/com_google_absl/absl/base/dynamic_annotations/dynamic_annotations.o
external/com_google_absl/absl/base/spinlock_wait/spinlock_wait.o
external/com_google_absl/absl/base/throw_delegate/throw_delegate.o
external/com_google_absl/absl/numeric/int128/int128.o
external/com_google_absl/absl/strings/internal/ostringstream.o
external/com_google_absl/absl/strings/internal/utf8.o
external/com_google_absl/absl/strings/strings/ascii.o
external/com_google_absl/absl/strings/strings/charconv.o
external/com_google_absl/absl/strings/strings/charconv_bigint.o
external/com_google_absl/absl/strings/strings/charconv_parse.o
external/com_google_absl/absl/strings/strings/escaping.o
external/com_google_absl/absl/strings/strings/match.o
external/com_google_absl/absl/strings/strings/memutil.o
external/com_google_absl/absl/strings/strings/numbers.o
external/com_google_absl/absl/strings/strings/str_cat.o
external/com_google_absl/absl/strings/strings/str_replace.o
external/com_google_absl/absl/strings/strings/str_split.o
external/com_google_absl/absl/strings/strings/string_view.o
external/com_google_absl/absl/strings/strings/substitute.o
tensorflow/core/lib_proto_parsing/protobuf.o
tensorflow/core/platform/cpu_info/cpu_info.o
tensorflow/core/platform/env_time/0/env_time.o
tensorflow/core/platform/env_time/1/env_time.o
tensorflow/core/platform/logging/logging.o
tensorflow/tools/proto_text/gen_proto_text_functions/gen_proto_text_functions.o
tensorflow/tools/proto_text/gen_proto_text_functions_lib/gen_proto_text_functions_lib.o
'''.split()

inputs1_proto_text = """
tensorflow/core tensorflow/core/ tensorflow/core/lib/core/error_codes.proto tensorflow/tools/proto_text/placeholder.txt
""".split()

inputs2_proto_text = """
tensorflow/core tensorflow/core/ tensorflow/core/example/example.proto tensorflow/core/example/feature.proto tensorflow/core/framework/allocation_description.proto tensorflow/core/framework/api_def.proto tensorflow/core/framework/attr_value.proto tensorflow/core/framework/cost_graph.proto tensorflow/core/framework/device_attributes.proto tensorflow/core/framework/function.proto tensorflow/core/framework/graph.proto tensorflow/core/framework/graph_transfer_info.proto tensorflow/core/framework/kernel_def.proto tensorflow/core/framework/log_memory.proto tensorflow/core/framework/node_def.proto tensorflow/core/framework/op_def.proto tensorflow/core/framework/reader_base.proto tensorflow/core/framework/remote_fused_graph_execute_info.proto tensorflow/core/framework/resource_handle.proto tensorflow/core/framework/step_stats.proto tensorflow/core/framework/summary.proto tensorflow/core/framework/tensor.proto tensorflow/core/framework/tensor_description.proto tensorflow/core/framework/tensor_shape.proto tensorflow/core/framework/tensor_slice.proto tensorflow/core/framework/types.proto tensorflow/core/framework/variable.proto tensorflow/core/framework/versions.proto tensorflow/core/protobuf/config.proto tensorflow/core/protobuf/cluster.proto tensorflow/core/protobuf/debug.proto tensorflow/core/protobuf/device_properties.proto tensorflow/core/protobuf/graph_debug_info.proto tensorflow/core/protobuf/queue_runner.proto tensorflow/core/protobuf/rewriter_config.proto tensorflow/core/protobuf/tensor_bundle.proto tensorflow/core/protobuf/saver.proto tensorflow/core/protobuf/verifier_config.proto tensorflow/core/protobuf/trace_events.proto tensorflow/core/util/event.proto tensorflow/core/util/memmapped_file_system.proto tensorflow/core/util/saved_tensor_slice.proto tensorflow/core/lib/core/error_codes.proto tensorflow/tools/proto_text/placeholder.txt
""".split()


objs_libtensorflow_framework = '''
external/com_google_absl/absl/base/base/cycleclock.pic.o
external/com_google_absl/absl/base/base/log_severity.pic.o
external/com_google_absl/absl/base/base/raw_logging.pic.o
external/com_google_absl/absl/base/base/spinlock.pic.o
external/com_google_absl/absl/base/base/sysinfo.pic.o
external/com_google_absl/absl/base/base/thread_identity.pic.o
external/com_google_absl/absl/base/base/unscaledcycleclock.pic.o
external/com_google_absl/absl/base/dynamic_annotations/dynamic_annotations.pic.o
external/com_google_absl/absl/base/malloc_internal/low_level_alloc.pic.o
external/com_google_absl/absl/base/spinlock_wait/spinlock_wait.pic.o
external/com_google_absl/absl/base/throw_delegate/throw_delegate.pic.o
external/com_google_absl/absl/container/hashtablez_sampler/hashtablez_sampler.pic.o
external/com_google_absl/absl/container/hashtablez_sampler/hashtablez_sampler_force_weak_definition.pic.o
external/com_google_absl/absl/container/raw_hash_set/raw_hash_set.pic.o
external/com_google_absl/absl/debugging/debugging_internal/address_is_readable.pic.o
external/com_google_absl/absl/debugging/debugging_internal/elf_mem_image.pic.o
external/com_google_absl/absl/debugging/debugging_internal/vdso_support.pic.o
external/com_google_absl/absl/debugging/demangle_internal/demangle.pic.o
external/com_google_absl/absl/debugging/stacktrace/stacktrace.pic.o
external/com_google_absl/absl/debugging/symbolize/symbolize.pic.o
external/com_google_absl/absl/hash/city/city.pic.o
external/com_google_absl/absl/hash/hash/hash.pic.o
external/com_google_absl/absl/numeric/int128/int128.pic.o
external/com_google_absl/absl/strings/internal/ostringstream.pic.o
external/com_google_absl/absl/strings/internal/utf8.pic.o
external/com_google_absl/absl/strings/str_format_internal/arg.pic.o
external/com_google_absl/absl/strings/str_format_internal/bind.pic.o
external/com_google_absl/absl/strings/str_format_internal/extension.pic.o
external/com_google_absl/absl/strings/str_format_internal/float_conversion.pic.o
external/com_google_absl/absl/strings/str_format_internal/output.pic.o
external/com_google_absl/absl/strings/str_format_internal/parser.pic.o
external/com_google_absl/absl/strings/strings/ascii.pic.o
external/com_google_absl/absl/strings/strings/charconv.pic.o
external/com_google_absl/absl/strings/strings/charconv_bigint.pic.o
external/com_google_absl/absl/strings/strings/charconv_parse.pic.o
external/com_google_absl/absl/strings/strings/escaping.pic.o
external/com_google_absl/absl/strings/strings/match.pic.o
external/com_google_absl/absl/strings/strings/memutil.pic.o
external/com_google_absl/absl/strings/strings/numbers.pic.o
external/com_google_absl/absl/strings/strings/str_cat.pic.o
external/com_google_absl/absl/strings/strings/str_replace.pic.o
external/com_google_absl/absl/strings/strings/str_split.pic.o
external/com_google_absl/absl/strings/strings/string_view.pic.o
external/com_google_absl/absl/strings/strings/substitute.pic.o
external/com_google_absl/absl/synchronization/graphcycles_internal/graphcycles.pic.o
external/com_google_absl/absl/synchronization/synchronization/barrier.pic.o
external/com_google_absl/absl/synchronization/synchronization/blocking_counter.pic.o
external/com_google_absl/absl/synchronization/synchronization/create_thread_identity.pic.o
external/com_google_absl/absl/synchronization/synchronization/mutex.pic.o
external/com_google_absl/absl/synchronization/synchronization/notification.pic.o
external/com_google_absl/absl/synchronization/synchronization/per_thread_sem.pic.o
external/com_google_absl/absl/synchronization/synchronization/waiter.pic.o
external/com_google_absl/absl/time/internal/cctz/civil_time/civil_time_detail.pic.o
external/com_google_absl/absl/time/internal/cctz/time_zone/time_zone_fixed.pic.o
external/com_google_absl/absl/time/internal/cctz/time_zone/time_zone_format.pic.o
external/com_google_absl/absl/time/internal/cctz/time_zone/time_zone_if.pic.o
external/com_google_absl/absl/time/internal/cctz/time_zone/time_zone_impl.pic.o
external/com_google_absl/absl/time/internal/cctz/time_zone/time_zone_info.pic.o
external/com_google_absl/absl/time/internal/cctz/time_zone/time_zone_libc.pic.o
external/com_google_absl/absl/time/internal/cctz/time_zone/time_zone_lookup.pic.o
external/com_google_absl/absl/time/internal/cctz/time_zone/time_zone_posix.pic.o
external/com_google_absl/absl/time/internal/cctz/time_zone/zone_info_source.pic.o
external/com_google_absl/absl/time/time/civil_time.pic.o
external/com_google_absl/absl/time/time/clock.pic.o
external/com_google_absl/absl/time/time/duration.pic.o
external/com_google_absl/absl/time/time/format.pic.o
external/com_google_absl/absl/time/time/time.pic.o
external/com_google_absl/absl/types/bad_optional_access/bad_optional_access.pic.o
external/com_google_absl/absl/types/bad_variant_access/bad_variant_access.pic.o
tensorflow/cc/saved_model/loader_lite_impl/loader.pic.o
tensorflow/cc/saved_model/reader/reader.pic.o
tensorflow/core/allocator/allocator.pic.o
tensorflow/core/allocator/tracking_allocator.pic.o
tensorflow/core/allocator_registry_impl/allocator_registry.pic.o
tensorflow/core/allocator_registry_impl/cpu_allocator_impl.pic.o
tensorflow/core/autotuning_proto_cc_impl/autotuning.pb.pic.o
tensorflow/core/bfc_allocator/allocator_retry.pic.o
tensorflow/core/bfc_allocator/bfc_allocator.pic.o
tensorflow/core/conv_autotuning_proto_cc_impl/conv_autotuning.pb.pic.o
tensorflow/core/core_cpu_base_no_ops/eval_const_tensor.pic.o
tensorflow/core/core_cpu_base_no_ops/graph_constructor.pic.o
tensorflow/core/core_cpu_base_no_ops/graph_def_builder_util.pic.o
tensorflow/core/core_cpu_base_no_ops/scoped_allocator.pic.o
tensorflow/core/core_cpu_base_no_ops/scoped_allocator_mgr.pic.o
tensorflow/core/core_cpu_base_no_ops/shape_refiner.pic.o
tensorflow/core/core_cpu_impl/accumulate_n_optimizer.pic.o
tensorflow/core/core_cpu_impl/base_collective_executor.pic.o
tensorflow/core/core_cpu_impl/buf_rendezvous.pic.o
tensorflow/core/core_cpu_impl/build_graph_options.pic.o
tensorflow/core/core_cpu_impl/collective_executor_mgr.pic.o
tensorflow/core/core_cpu_impl/collective_param_resolver_local.pic.o
tensorflow/core/core_cpu_impl/collective_rma_local.pic.o
tensorflow/core/core_cpu_impl/collective_util.pic.o
tensorflow/core/core_cpu_impl/colocation_graph.pic.o
tensorflow/core/core_cpu_impl/constant_folding.pic.o
tensorflow/core/core_cpu_impl/copy_tensor.pic.o
tensorflow/core/core_cpu_impl/costmodel_manager.pic.o
tensorflow/core/core_cpu_impl/debugger_state_interface.pic.o
tensorflow/core/core_cpu_impl/device.pic.o
tensorflow/core/core_cpu_impl/device_factory.pic.o
tensorflow/core/core_cpu_impl/device_mgr.pic.o
tensorflow/core/core_cpu_impl/device_resolver_local.pic.o
tensorflow/core/core_cpu_impl/device_set.pic.o
tensorflow/core/core_cpu_impl/executor.pic.o
tensorflow/core/core_cpu_impl/executor_factory.pic.o
tensorflow/core/core_cpu_impl/function.pic.o
tensorflow/core/core_cpu_impl/gradients.pic.o
tensorflow/core/core_cpu_impl/graph_optimizer.pic.o
tensorflow/core/core_cpu_impl/graph_runner.pic.o
tensorflow/core/core_cpu_impl/hierarchical_tree_broadcaster.pic.o
tensorflow/core/core_cpu_impl/input_colocation_exemption_registry.pic.o
tensorflow/core/core_cpu_impl/inspecting_placer.pic.o
tensorflow/core/core_cpu_impl/isolate_placer_inspection_required_ops_pass.pic.o
tensorflow/core/core_cpu_impl/local_device.pic.o
tensorflow/core/core_cpu_impl/lower_case_op.pic.o
tensorflow/core/core_cpu_impl/lower_function_call_op.pic.o
tensorflow/core/core_cpu_impl/lower_functional_ops.pic.o
tensorflow/core/core_cpu_impl/lower_if_op.pic.o
tensorflow/core/core_cpu_impl/lower_while_op.pic.o
tensorflow/core/core_cpu_impl/memory_types.pic.o
tensorflow/core/core_cpu_impl/metrics.pic.o
tensorflow/core/core_cpu_impl/mkl_cpu_allocator.pic.o
tensorflow/core/core_cpu_impl/mkl_layout_pass.pic.o
tensorflow/core/core_cpu_impl/mkl_tfconversion_pass.pic.o
tensorflow/core/core_cpu_impl/optimization_registry.pic.o
tensorflow/core/core_cpu_impl/parallel_concat_optimizer.pic.o
tensorflow/core/core_cpu_impl/partitioning_utils.pic.o
tensorflow/core/core_cpu_impl/placer.pic.o
tensorflow/core/core_cpu_impl/placer_inspection_required_ops_utils.pic.o
tensorflow/core/core_cpu_impl/pool_allocator.pic.o
tensorflow/core/core_cpu_impl/process_function_library_runtime.pic.o
tensorflow/core/core_cpu_impl/process_state.pic.o
tensorflow/core/core_cpu_impl/process_util.pic.o
tensorflow/core/core_cpu_impl/quantize_training.pic.o
tensorflow/core/core_cpu_impl/renamed_device.pic.o
tensorflow/core/core_cpu_impl/rendezvous_mgr.pic.o
tensorflow/core/core_cpu_impl/rendezvous_util.pic.o
tensorflow/core/core_cpu_impl/ring_alg.pic.o
tensorflow/core/core_cpu_impl/ring_gatherer.pic.o
tensorflow/core/core_cpu_impl/ring_reducer.pic.o
tensorflow/core/core_cpu_impl/session.pic.o
tensorflow/core/core_cpu_impl/session_factory.pic.o
tensorflow/core/core_cpu_impl/session_options.pic.o
tensorflow/core/core_cpu_impl/session_state.pic.o
tensorflow/core/core_cpu_impl/single_threaded_cpu_device.pic.o
tensorflow/core/core_cpu_impl/stats_publisher_interface.pic.o
tensorflow/core/core_cpu_impl/step_stats_collector.pic.o
tensorflow/core/core_cpu_impl/threadpool_device.pic.o
tensorflow/core/core_cpu_impl/threadpool_device_factory.pic.o
tensorflow/core/core_cpu_internal/graph_execution_state.pic.o
tensorflow/core/error_codes_proto_cc_impl/error_codes.pb.pic.o
tensorflow/core/error_codes_proto_text/error_codes.pb_text.pic.o
tensorflow/core/feature_util/feature_util.pic.o
tensorflow/core/framework_internal_impl/activation_mode.pic.o
tensorflow/core/framework_internal_impl/attr_value_util.pic.o
tensorflow/core/framework_internal_impl/batch_util.pic.o
tensorflow/core/framework_internal_impl/bcast.pic.o
tensorflow/core/framework_internal_impl/bfloat16.pic.o
tensorflow/core/framework_internal_impl/cancellation.pic.o
tensorflow/core/framework_internal_impl/collective.pic.o
tensorflow/core/framework_internal_impl/command_line_flags.pic.o
tensorflow/core/framework_internal_impl/common_shape_fns.pic.o
tensorflow/core/framework_internal_impl/dataset.pic.o
tensorflow/core/framework_internal_impl/device_base.pic.o
tensorflow/core/framework_internal_impl/device_name_utils.pic.o
tensorflow/core/framework_internal_impl/dump_graph.pic.o
tensorflow/core/framework_internal_impl/edgeset.pic.o
tensorflow/core/framework_internal_impl/einsum_op_util.pic.o
tensorflow/core/framework_internal_impl/equal_graph_def.pic.o
tensorflow/core/framework_internal_impl/events_writer.pic.o
tensorflow/core/framework_internal_impl/example_proto_fast_parsing.pic.o
tensorflow/core/framework_internal_impl/example_proto_helper.pic.o
tensorflow/core/framework_internal_impl/function.pic.o
tensorflow/core/framework_internal_impl/function_handle_cache.pic.o
tensorflow/core/framework_internal_impl/graph.pic.o
tensorflow/core/framework_internal_impl/graph_def_builder.pic.o
tensorflow/core/framework_internal_impl/graph_def_util.pic.o
tensorflow/core/framework_internal_impl/graph_to_functiondef.pic.o
tensorflow/core/framework_internal_impl/group_iterator.pic.o
tensorflow/core/framework_internal_impl/guarded_philox_random.pic.o
tensorflow/core/framework_internal_impl/kernel_def_builder.pic.o
tensorflow/core/framework_internal_impl/kernel_def_util.pic.o
tensorflow/core/framework_internal_impl/load_library.pic.o
tensorflow/core/framework_internal_impl/log_memory.pic.o
tensorflow/core/framework_internal_impl/logging.pic.o
tensorflow/core/framework_internal_impl/lookup_interface.pic.o
tensorflow/core/framework_internal_impl/matmul_autotune.pic.o
tensorflow/core/framework_internal_impl/matmul_bcast.pic.o
tensorflow/core/framework_internal_impl/memmapped_file_system.pic.o
tensorflow/core/framework_internal_impl/memmapped_file_system_writer.pic.o
tensorflow/core/framework_internal_impl/memory_types.pic.o
tensorflow/core/framework_internal_impl/mirror_pad_mode.pic.o
tensorflow/core/framework_internal_impl/model.pic.o
tensorflow/core/framework_internal_impl/node_builder.pic.o
tensorflow/core/framework_internal_impl/node_def_builder.pic.o
tensorflow/core/framework_internal_impl/node_def_util.pic.o
tensorflow/core/framework_internal_impl/op.pic.o
tensorflow/core/framework_internal_impl/op_def_builder.pic.o
tensorflow/core/framework_internal_impl/op_def_util.pic.o
tensorflow/core/framework_internal_impl/op_kernel.pic.o
tensorflow/core/framework_internal_impl/op_segment.pic.o
tensorflow/core/framework_internal_impl/ops_util.pic.o
tensorflow/core/framework_internal_impl/padding.pic.o
tensorflow/core/framework_internal_impl/port.pic.o
tensorflow/core/framework_internal_impl/rendezvous.pic.o
tensorflow/core/framework_internal_impl/resource_handle.pic.o
tensorflow/core/framework_internal_impl/resource_mgr.pic.o
tensorflow/core/framework_internal_impl/run_handler.pic.o
tensorflow/core/framework_internal_impl/run_handler_util.pic.o
tensorflow/core/framework_internal_impl/saved_tensor_slice_util.pic.o
tensorflow/core/framework_internal_impl/shape_inference.pic.o
tensorflow/core/framework_internal_impl/stat_summarizer.pic.o
tensorflow/core/framework_internal_impl/strided_slice_op.pic.o
tensorflow/core/framework_internal_impl/tensor.pic.o
tensorflow/core/framework_internal_impl/tensor_format.pic.o
tensorflow/core/framework_internal_impl/tensor_id.pic.o
tensorflow/core/framework_internal_impl/tensor_reference.pic.o
tensorflow/core/framework_internal_impl/tensor_shape.pic.o
tensorflow/core/framework_internal_impl/tensor_slice.pic.o
tensorflow/core/framework_internal_impl/tensor_slice_reader.pic.o
tensorflow/core/framework_internal_impl/tensor_slice_reader_cache.pic.o
tensorflow/core/framework_internal_impl/tensor_slice_set.pic.o
tensorflow/core/framework_internal_impl/tensor_slice_writer.pic.o
tensorflow/core/framework_internal_impl/tensor_util.pic.o
tensorflow/core/framework_internal_impl/typed_allocator.pic.o
tensorflow/core/framework_internal_impl/types.pic.o
tensorflow/core/framework_internal_impl/unique_tensor_references.pic.o
tensorflow/core/framework_internal_impl/use_cudnn.pic.o
tensorflow/core/framework_internal_impl/util.pic.o
tensorflow/core/framework_internal_impl/variant.pic.o
tensorflow/core/framework_internal_impl/variant_op_registry.pic.o
tensorflow/core/framework_internal_impl/variant_tensor_data.pic.o
tensorflow/core/framework_internal_impl/versions.pic.o
tensorflow/core/framework_internal_impl/while_context.pic.o
tensorflow/core/framework_internal_impl/work_sharder.pic.o
tensorflow/core/gpu_bfc_allocator/gpu_bfc_allocator.pic.o
tensorflow/core/gpu_id_impl/gpu_id_manager.pic.o
tensorflow/core/gpu_init_impl/gpu_init.pic.o
tensorflow/core/gpu_lib/gpu_event_mgr.pic.o
tensorflow/core/gpu_runtime_impl/gpu_cudamalloc_allocator.pic.o
tensorflow/core/gpu_runtime_impl/gpu_debug_allocator.pic.o
tensorflow/core/gpu_runtime_impl/gpu_device.pic.o
tensorflow/core/gpu_runtime_impl/gpu_device_factory.pic.o
tensorflow/core/gpu_runtime_impl/gpu_managed_allocator.pic.o
tensorflow/core/gpu_runtime_impl/gpu_process_state.pic.o
tensorflow/core/gpu_runtime_impl/gpu_stream_util.pic.o
tensorflow/core/gpu_runtime_impl/gpu_util.pic.o
tensorflow/core/gpu_runtime_impl/gpu_util_platform_specific.pic.o
tensorflow/core/graph/algorithm.pic.o
tensorflow/core/graph/collective_order.pic.o
tensorflow/core/graph/colors.pic.o
tensorflow/core/graph/control_flow.pic.o
tensorflow/core/graph/costmodel.pic.o
tensorflow/core/graph/graph_partition.pic.o
tensorflow/core/graph/optimizer_cse.pic.o
tensorflow/core/graph/subgraph.pic.o
tensorflow/core/graph/validate.pic.o
tensorflow/core/grappler/clusters/cluster/cluster.pic.o
tensorflow/core/grappler/clusters/utils/utils.pic.o
tensorflow/core/grappler/clusters/virtual_cluster/virtual_cluster.pic.o
tensorflow/core/grappler/costs/analytical_cost_estimator/analytical_cost_estimator.pic.o
tensorflow/core/grappler/costs/cost_estimator/cost_estimator.pic.o
tensorflow/core/grappler/costs/graph_memory/graph_memory.pic.o
tensorflow/core/grappler/costs/graph_properties/graph_properties.pic.o
tensorflow/core/grappler/costs/op_level_cost_estimator/op_level_cost_estimator.pic.o
tensorflow/core/grappler/costs/op_performance_data_cc_impl/op_performance_data.pb.pic.o
tensorflow/core/grappler/costs/utils/utils.pic.o
tensorflow/core/grappler/costs/virtual_placer/virtual_placer.pic.o
tensorflow/core/grappler/costs/virtual_scheduler/virtual_scheduler.pic.o
tensorflow/core/grappler/devices/devices.pic.o
tensorflow/core/grappler/graph_topology_view/graph_topology_view.pic.o
tensorflow/core/grappler/graph_view/graph_view.pic.o
tensorflow/core/grappler/grappler_item/grappler_item.pic.o
tensorflow/core/grappler/mutable_graph_view/mutable_graph_view.pic.o
tensorflow/core/grappler/op_types/op_types.pic.o
tensorflow/core/grappler/optimizers/arithmetic_optimizer/arithmetic_optimizer.pic.o
tensorflow/core/grappler/optimizers/auto_mixed_precision/auto_mixed_precision.pic.o
tensorflow/core/grappler/optimizers/auto_parallel/auto_parallel.pic.o
tensorflow/core/grappler/optimizers/constant_folding/constant_folding.pic.o
tensorflow/core/grappler/optimizers/custom_graph_optimizer_registry_impl/custom_graph_optimizer_registry.pic.o
tensorflow/core/grappler/optimizers/debug_stripper/debug_stripper.pic.o
tensorflow/core/grappler/optimizers/dependency_optimizer/dependency_optimizer.pic.o
tensorflow/core/grappler/optimizers/evaluation_utils/evaluation_utils.pic.o
tensorflow/core/grappler/optimizers/function_api_info/function_api_info.pic.o
tensorflow/core/grappler/optimizers/function_optimizer/function_optimizer.pic.o
tensorflow/core/grappler/optimizers/generic_layout_optimizer/generic_layout_optimizer.pic.o
tensorflow/core/grappler/optimizers/generic_layout_optimizer_transposer/generic_layout_optimizer_transposer.pic.o
tensorflow/core/grappler/optimizers/generic_layout_optimizer_transposer_factory/generic_layout_optimizer_transposer_factory.pic.o
tensorflow/core/grappler/optimizers/graph_optimizer_stage/graph_optimizer_stage.pic.o
tensorflow/core/grappler/optimizers/implementation_selector/implementation_selector.pic.o
tensorflow/core/grappler/optimizers/loop_optimizer/loop_optimizer.pic.o
tensorflow/core/grappler/optimizers/memory_optimizer/memory_optimizer.pic.o
tensorflow/core/grappler/optimizers/meta_optimizer/meta_optimizer.pic.o
tensorflow/core/grappler/optimizers/model_pruner/model_pruner.pic.o
tensorflow/core/grappler/optimizers/pin_to_host_optimizer/pin_to_host_optimizer.pic.o
tensorflow/core/grappler/optimizers/remapper/remapper.pic.o
tensorflow/core/grappler/optimizers/scoped_allocator_optimizer/scoped_allocator_optimizer.pic.o
tensorflow/core/grappler/optimizers/shape_optimizer/shape_optimizer.pic.o
tensorflow/core/grappler/optimizers/static_schedule/static_schedule.pic.o
tensorflow/core/grappler/utils/canonicalizer/canonicalizer.pic.o
tensorflow/core/grappler/utils/colocation/colocation.pic.o
tensorflow/core/grappler/utils/frame/frame.pic.o
tensorflow/core/grappler/utils/functions/functions.pic.o
tensorflow/core/grappler/utils/graph_view/graph_view.pic.o
tensorflow/core/grappler/utils/symbolic_shapes/symbolic_shapes.pic.o
tensorflow/core/grappler/utils/topological_sort/topological_sort.pic.o
tensorflow/core/grappler/utils/tpu/tpu.pic.o
tensorflow/core/grappler/utils/traversal/traversal.pic.o
tensorflow/core/grappler/utils/utils.pic.o
tensorflow/core/grappler/verifiers/structure_verifier/structure_verifier.pic.o
tensorflow/core/kernels/initializable_lookup_table/initializable_lookup_table.pic.o
tensorflow/core/kernels/lookup_util/lookup_util.pic.o
tensorflow/core/lib_hash_crc32c_accelerate_internal/crc32c_accelerate.pic.o
tensorflow/core/lib_internal_impl/0/env.pic.o
tensorflow/core/lib_internal_impl/0/tracing.pic.o
tensorflow/core/lib_internal_impl/1/env.pic.o
tensorflow/core/lib_internal_impl/1/tracing.pic.o
tensorflow/core/lib_internal_impl/android_armv7a_cpu_utils_helper.pic.o
tensorflow/core/lib_internal_impl/arena.pic.o
tensorflow/core/lib_internal_impl/base64.pic.o
tensorflow/core/lib_internal_impl/bfloat16.pic.o
tensorflow/core/lib_internal_impl/bitmap.pic.o
tensorflow/core/lib_internal_impl/block.pic.o
tensorflow/core/lib_internal_impl/block_builder.pic.o
tensorflow/core/lib_internal_impl/buffered_inputstream.pic.o
tensorflow/core/lib_internal_impl/clock_cycle_profiler.pic.o
tensorflow/core/lib_internal_impl/coding.pic.o
tensorflow/core/lib_internal_impl/collection_registry.pic.o
tensorflow/core/lib_internal_impl/compression.pic.o
tensorflow/core/lib_internal_impl/cpu_feature_guard.pic.o
tensorflow/core/lib_internal_impl/cpu_utils.pic.o
tensorflow/core/lib_internal_impl/crc32c.pic.o
tensorflow/core/lib_internal_impl/denormal.pic.o
tensorflow/core/lib_internal_impl/distribution_sampler.pic.o
tensorflow/core/lib_internal_impl/env_var.pic.o
tensorflow/core/lib_internal_impl/error.pic.o
tensorflow/core/lib_internal_impl/file_system.pic.o
tensorflow/core/lib_internal_impl/file_system_helper.pic.o
tensorflow/core/lib_internal_impl/format.pic.o
tensorflow/core/lib_internal_impl/hash.pic.o
tensorflow/core/lib_internal_impl/histogram.pic.o
tensorflow/core/lib_internal_impl/inputbuffer.pic.o
tensorflow/core/lib_internal_impl/inputstream_interface.pic.o
tensorflow/core/lib_internal_impl/iterator.pic.o
tensorflow/core/lib_internal_impl/load_library.pic.o
tensorflow/core/lib_internal_impl/monitoring.pic.o
tensorflow/core/lib_internal_impl/mutex.pic.o
tensorflow/core/lib_internal_impl/net.pic.o
tensorflow/core/lib_internal_impl/numbers.pic.o
tensorflow/core/lib_internal_impl/ordered_code.pic.o
tensorflow/core/lib_internal_impl/path.pic.o
tensorflow/core/lib_internal_impl/port.pic.o
tensorflow/core/lib_internal_impl/posix_file_system.pic.o
tensorflow/core/lib_internal_impl/proto_serialization.pic.o
tensorflow/core/lib_internal_impl/proto_text_util.pic.o
tensorflow/core/lib_internal_impl/protobuf_util.pic.o
tensorflow/core/lib_internal_impl/random.pic.o
tensorflow/core/lib_internal_impl/random_distributions.pic.o
tensorflow/core/lib_internal_impl/random_inputstream.pic.o
tensorflow/core/lib_internal_impl/record_reader.pic.o
tensorflow/core/lib_internal_impl/record_writer.pic.o
tensorflow/core/lib_internal_impl/sampler.pic.o
tensorflow/core/lib_internal_impl/scanner.pic.o
tensorflow/core/lib_internal_impl/setround.pic.o
tensorflow/core/lib_internal_impl/simple_philox.pic.o
tensorflow/core/lib_internal_impl/snappy_inputbuffer.pic.o
tensorflow/core/lib_internal_impl/snappy_outputbuffer.pic.o
tensorflow/core/lib_internal_impl/stacktrace_handler.pic.o
tensorflow/core/lib_internal_impl/status.pic.o
tensorflow/core/lib_internal_impl/str_util.pic.o
tensorflow/core/lib_internal_impl/strcat.pic.o
tensorflow/core/lib_internal_impl/stringprintf.pic.o
tensorflow/core/lib_internal_impl/subprocess.pic.o
tensorflow/core/lib_internal_impl/table.pic.o
tensorflow/core/lib_internal_impl/table_builder.pic.o
tensorflow/core/lib_internal_impl/tensor_coding.pic.o
tensorflow/core/lib_internal_impl/threadpool.pic.o
tensorflow/core/lib_internal_impl/two_level_iterator.pic.o
tensorflow/core/lib_internal_impl/unbounded_work_queue.pic.o
tensorflow/core/lib_internal_impl/wav_io.pic.o
tensorflow/core/lib_internal_impl/weighted_picker.pic.o
tensorflow/core/lib_internal_impl/zlib_compression_options.pic.o
tensorflow/core/lib_internal_impl/zlib_inputstream.pic.o
tensorflow/core/lib_internal_impl/zlib_outputbuffer.pic.o
tensorflow/core/lib_proto_parsing/protobuf.pic.o
tensorflow/core/platform/abi/abi.pic.o
tensorflow/core/platform/cloud/compute_engine_metadata_client/compute_engine_metadata_client.pic.o
tensorflow/core/platform/cloud/compute_engine_zone_provider/compute_engine_zone_provider.pic.o
tensorflow/core/platform/cloud/curl_http_request/curl_http_request.pic.o
tensorflow/core/platform/cloud/gcs_dns_cache/gcs_dns_cache.pic.o
tensorflow/core/platform/cloud/gcs_file_system/gcs_file_system.pic.o
tensorflow/core/platform/cloud/gcs_throttle/gcs_throttle.pic.o
tensorflow/core/platform/cloud/google_auth_provider/google_auth_provider.pic.o
tensorflow/core/platform/cloud/oauth_client/oauth_client.pic.o
tensorflow/core/platform/cloud/ram_file_block_cache/ram_file_block_cache.pic.o
tensorflow/core/platform/cloud/retrying_utils/retrying_utils.pic.o
tensorflow/core/platform/cloud/time_util/time_util.pic.o
tensorflow/core/platform/cpu_info/cpu_info.pic.o
tensorflow/core/platform/env_time/0/env_time.pic.o
tensorflow/core/platform/env_time/1/env_time.pic.o
tensorflow/core/platform/hadoop/hadoop_file_system/hadoop_file_system.pic.o
tensorflow/core/platform/logging/logging.pic.o
tensorflow/core/platform_strings/platform_strings.pic.o
tensorflow/core/profiler/internal/traceme_recorder/traceme_recorder.pic.o
tensorflow/core/profiler/lib/traceme/traceme.pic.o
tensorflow/core/protos_all_proto_cc_impl/allocation_description.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/api_def.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/attr_value.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/cluster.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/config.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/control_flow.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/cost_graph.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/debug.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/device_attributes.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/device_properties.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/event.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/example.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/example_parser_configuration.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/feature.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/function.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/graph.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/graph_debug_info.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/graph_transfer_info.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/kernel_def.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/log_memory.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/memmapped_file_system.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/meta_graph.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/named_tensor.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/node_def.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/op_def.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/queue_runner.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/reader_base.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/remote_fused_graph_execute_info.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/resource_handle.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/rewriter_config.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/saved_model.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/saved_object_graph.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/saved_tensor_slice.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/saver.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/snapshot.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/step_stats.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/struct.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/summary.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/tensor.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/tensor_bundle.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/tensor_description.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/tensor_shape.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/tensor_slice.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/tensorflow_server.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/test_log.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/trace_events.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/trackable_object_graph.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/transport_options.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/types.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/variable.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/verifier_config.pb.pic.o
tensorflow/core/protos_all_proto_cc_impl/versions.pb.pic.o
tensorflow/core/protos_all_proto_text/allocation_description.pb_text.pic.o
tensorflow/core/protos_all_proto_text/api_def.pb_text.pic.o
tensorflow/core/protos_all_proto_text/attr_value.pb_text.pic.o
tensorflow/core/protos_all_proto_text/cluster.pb_text.pic.o
tensorflow/core/protos_all_proto_text/config.pb_text.pic.o
tensorflow/core/protos_all_proto_text/cost_graph.pb_text.pic.o
tensorflow/core/protos_all_proto_text/debug.pb_text.pic.o
tensorflow/core/protos_all_proto_text/device_attributes.pb_text.pic.o
tensorflow/core/protos_all_proto_text/device_properties.pb_text.pic.o
tensorflow/core/protos_all_proto_text/event.pb_text.pic.o
tensorflow/core/protos_all_proto_text/example.pb_text.pic.o
tensorflow/core/protos_all_proto_text/feature.pb_text.pic.o
tensorflow/core/protos_all_proto_text/function.pb_text.pic.o
tensorflow/core/protos_all_proto_text/graph.pb_text.pic.o
tensorflow/core/protos_all_proto_text/graph_debug_info.pb_text.pic.o
tensorflow/core/protos_all_proto_text/graph_transfer_info.pb_text.pic.o
tensorflow/core/protos_all_proto_text/kernel_def.pb_text.pic.o
tensorflow/core/protos_all_proto_text/log_memory.pb_text.pic.o
tensorflow/core/protos_all_proto_text/memmapped_file_system.pb_text.pic.o
tensorflow/core/protos_all_proto_text/node_def.pb_text.pic.o
tensorflow/core/protos_all_proto_text/op_def.pb_text.pic.o
tensorflow/core/protos_all_proto_text/queue_runner.pb_text.pic.o
tensorflow/core/protos_all_proto_text/reader_base.pb_text.pic.o
tensorflow/core/protos_all_proto_text/remote_fused_graph_execute_info.pb_text.pic.o
tensorflow/core/protos_all_proto_text/resource_handle.pb_text.pic.o
tensorflow/core/protos_all_proto_text/rewriter_config.pb_text.pic.o
tensorflow/core/protos_all_proto_text/saved_tensor_slice.pb_text.pic.o
tensorflow/core/protos_all_proto_text/saver.pb_text.pic.o
tensorflow/core/protos_all_proto_text/step_stats.pb_text.pic.o
tensorflow/core/protos_all_proto_text/summary.pb_text.pic.o
tensorflow/core/protos_all_proto_text/tensor.pb_text.pic.o
tensorflow/core/protos_all_proto_text/tensor_bundle.pb_text.pic.o
tensorflow/core/protos_all_proto_text/tensor_description.pb_text.pic.o
tensorflow/core/protos_all_proto_text/tensor_shape.pb_text.pic.o
tensorflow/core/protos_all_proto_text/tensor_slice.pb_text.pic.o
tensorflow/core/protos_all_proto_text/trace_events.pb_text.pic.o
tensorflow/core/protos_all_proto_text/types.pb_text.pic.o
tensorflow/core/protos_all_proto_text/variable.pb_text.pic.o
tensorflow/core/protos_all_proto_text/verifier_config.pb_text.pic.o
tensorflow/core/protos_all_proto_text/versions.pb_text.pic.o
tensorflow/core/stats_calculator_portable/stats_calculator.pic.o
tensorflow/core/util/tensor_bundle/naming/naming.pic.o
tensorflow/core/util/tensor_bundle/tensor_bundle/byte_swap.pic.o
tensorflow/core/util/tensor_bundle/tensor_bundle/tensor_bundle.pic.o
tensorflow/core/version_lib/version_info.pic.o
tensorflow/stream_executor/allocator_stats/allocator_stats.pic.o
tensorflow/stream_executor/blas/blas.pic.o
tensorflow/stream_executor/cuda/cuda_platform_id/cuda_platform_id.pic.o
tensorflow/stream_executor/device_description/device_description.pic.o
tensorflow/stream_executor/dnn/dnn.pic.o
tensorflow/stream_executor/dnn_proto_cc_impl/dnn.pb.pic.o
tensorflow/stream_executor/event/event.pic.o
tensorflow/stream_executor/executor_cache/executor_cache.pic.o
tensorflow/stream_executor/host/host_platform_id/host_platform_id.pic.o
tensorflow/stream_executor/kernel/kernel.pic.o
tensorflow/stream_executor/kernel_spec/kernel_spec.pic.o
tensorflow/stream_executor/lib/lib/demangle.pic.o
tensorflow/stream_executor/lib/lib/numbers.pic.o
tensorflow/stream_executor/lib/lib/path.pic.o
tensorflow/stream_executor/lib/lib/process_state.pic.o
tensorflow/stream_executor/lib/lib/statusor.pic.o
tensorflow/stream_executor/multi_platform_manager/multi_platform_manager.pic.o
tensorflow/stream_executor/platform/default/dso_loader/dlopen_checker.pic.o
tensorflow/stream_executor/platform/default/dso_loader/dso_loader.pic.o
tensorflow/stream_executor/platform/platform.pic.o
tensorflow/stream_executor/plugin/plugin.pic.o
tensorflow/stream_executor/plugin_registry/plugin_registry.pic.o
tensorflow/stream_executor/rng/rng.pic.o
tensorflow/stream_executor/rocm/rocm_platform_id/rocm_platform_id.pic.o
tensorflow/stream_executor/scratch_allocator/scratch_allocator.pic.o
tensorflow/stream_executor/stream/stream.pic.o
tensorflow/stream_executor/stream_executor_internal/stream_executor_internal.pic.o
tensorflow/stream_executor/stream_executor_pimpl/stream_executor_pimpl.pic.o
tensorflow/stream_executor/temporary_device_memory/temporary_device_memory.pic.o
tensorflow/stream_executor/temporary_memory_manager/temporary_memory_manager.pic.o
tensorflow/stream_executor/timer/timer.pic.o
'''.split() 








class FakeBazel(object):
    @staticmethod
    def dirMangle(path: str):
        path = path.replace('bazel-out/k8-opt/bin/', '')
        path = path.replace('bazel-out/k8-opt/bin', './')
        path = path.replace('bazel-out/host/bin/', '')
        path = path.replace('bazel-out/host/bin', './')
        path = path.replace('/_objs/', '/')
        return path
    @staticmethod
    def parseBuildlog(path: str) -> List[str]:
        '''
        Read the Bazel buildlog (bazel build -s //tensorflow:xxx 2>&1 | tee log),
        collect all the command lines inside it and return the cmdline list.
        '''
        cmdlines = []
        lines = open(path, 'rt').readlines()
        states = [0, 0] # (anther SUBCOMMAND, bracket balance)
        for line in lines:
            if line.startswith('#') and line.endswith(')'): continue
            if line.startswith('WARNING:'): continue
            line = line.strip()
            if line.startswith('SUBCOMMAND'):
                if states[0] == 1:
                    states[0] = 0
            if line.endswith(')') and not line.endswith('__)') and \
                    not line.startswith('#') and not line.endswith('configured)'):
                if 'EOF' in line:
                    states[0] = 1
                elif states[0] == 0:
                    cmdlines.append(re.sub('\)$', '', line))
                    states[0] = 1
                else:
                    pass
        return cmdlines
    @staticmethod
    def understandCmdlines(cmdlines: List[str]) -> (List):
        '''
        Understand the command lines and rebuild the dependency graph.
        paths must be mangled.
        '''
        depgraph = []
        for cmd in cmdlines:
            if cmd.startswith('/usr/lib/ccache/gcc'):
                # it's a CXX/LD command
                target = {'type': 'CXX', 'src': [], 'obj': [], 'flags': []}
                tokens = shlex.split(cmd)
                for (i,t) in enumerate(tokens[1:], 1):
                    if any(re.match(r, t) for r in [
                        '-g\d',
                        '-c',
                        '-o',
                        '-O\d',
                        '-M\w',
                        '-m.*',
                        '-U_FORTIFY_SOURCE',
                        "-D__TIME__=.*?",
                        "-D__TIMESTAMP__=.*?",
                        "-D__DATE__=.*?",
                        '-D_FORTIFY_SOURCE=1',
                        '-Iexternal/.*',
                        '-I.',
                        '-B.*',
                        ]):
                        pass
                    elif any(re.match(r, t) for r in [
                        '-fstack-protect',
                        '-fno-omit-frame-pointer',
                        '-ffunction-sections',
                        '-fdata-sections',
                        '-fno-canonical-system-headers',
                        '-frandom-seed=.*',
                        '-fexceptions',
                        '-fno-exceptions',
                        '-ftemplate-depth.*',
                        '-fno-com.*',
                        '-fuse-ld.*',
                        ]):
                        pass
                    elif any(re.match(r, t) for r in [
                        '-Wall',
                        '-Woverloaded-virtual',
                        '-Wunused-but-set-parameter',
                        '-Wno-free-nonheap-object',
                        '-Wno-shift-negative-value',
                        '-Wno-builtin-macro-redefined',
                        '-Wno-sign-compare',
                        '-Wno-unused-function',
                        '-Wno-write-strings',
                        '-Wextra',
                        '-Wcast-qual',
                        '-Wconversion-null',
                        '-Wmissing-declarations',
                        '-Woverlength-strings',
                        '-Wpointer-arith',
                        '-Wunused-local-typedefs',
                        '-Wunused-result',
                        '-Wvarargs',
                        '-Wvla',
                        '-Wwrite-strings',
                        '-Wno-missing-field-initializers',
                        '-Wa,--noexecstack',
                        '-Werror',
                        '-Wformat=.*',
                        '-Wsign-compare',
                        '-Wmissing.*',
                        '-Wshadow.*',
                        '-Wold-st.*',
                        '-Wstrict.*',
                        '-Wno.*',
                        '-w', # Inhibit all warning messages. https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#Warning-Options
                        '-Wl,-rpath,.*',
                        ]):
                        pass
                    elif any(re.match(r, t) for r in [
                        '-D\S+',
                        '-pthread',
                        '-fPIC',
                        '-std=.*',
                        '-Wl.*',
                        '-pass-exit-codes',
                        '-shared',
                        ]):
                        target['flags'].append(FakeBazel.dirMangle(t))
                    elif re.match('-iquote', t) or re.match('-iquote', tokens[i-1]):
                        pass
                    elif re.match('-isystem', t) or re.match('-isystem', tokens[i-1]):
                        pass
                    elif re.match('-x', t) or re.match('-x', tokens[i-1]):
                        pass
                    elif re.match('.*\.d$', t):
                        pass
                    elif re.match('.*\.c[cp]?p?$', t):
                        target['src'].append(FakeBazel.dirMangle(t))
                    elif re.match('.*\.S$', t):
                        target['src'].append(FakeBazel.dirMangle(t))
                    elif re.match('-o', tokens[i-1]):
                        target['obj'].append(FakeBazel.dirMangle(t))
                    else:
                        raise Exception(f'what is {t}? prev={tokens[i-1]} next={tokens[i+1]} full={tokens}')
                if DEBUG: print(target)
                depgraph.append(target)
            elif cmd.startswith('/bin/bash -c'):
                # it's a shell command
                target = {'type': 'CMD', 'cmd': []}
                target['cmd'] = shlex.split(cmd)[-1]
                if DEBUG: print(target)
                depgraph.append(target)
            elif cmd.startswith('bazel-out/host/bin/external/nasm/nasm'):
                # we don't need this assember
                continue
            elif cmd.startswith('bazel-out/host/bin/external/com_google_protobuf/protoc'):
                # it's a protobuf compiler command
                target = {'type': 'PROTOC', 'proto': [], 'flags': []}
                tokens = shlex.split(cmd)
                for t in tokens[1:]:
                    if re.match('-I.*', t):
                        pass
                    elif re.match('--cpp_out=.*', t):
                        target['flags'].append(FakeBazel.dirMangle(t))
                    elif re.match('.*\.proto$', t):
                        target['proto'].append(FakeBazel.dirMangle(t))
                    else:
                        raise Exception(f'what is {t} in {cmd}?')
                if DEBUG: print(target)
                depgraph.append(target)
            else:
                raise Exception(f"cannot understand: {cmd}")
        return depgraph
    @staticmethod
    def rinseGraph(depgraph: List[str]) -> List[str]:
        '''
        Remove unwanted targets from the dependency graph,
        especially those for external source files (e.g. protobuf)
        '''
        G = []
        for t in depgraph:
            if 'CXX' == t['type']:
                if t['obj'][0] =='external/com_google_protobuf/protoc':
                    continue
                if t['obj'][0] =='external/nasm/nasm':
                    continue
                if len(t['src'])==0:
                    pass
                elif any(re.match(r, t['src'][0]) for r in[
                        'external/com_google_protobuf/.*',
                        'external/boringssl/.*',
                        'external/aws/.*',
                        #'external/com_google_absl/.*',
                        'external/curl/.*',
                        'external/fft2d/.*',
                        'external/com_googlesource_code_re2/.*',
                        'external/nsync/.*',
                        'external/jpeg/.*',
                        'external/hwloc/.*',
                        'external/gif_archive/.*',
                        'external/zlib_archive/.*',
                        'external/double_conversion/.*',
                        'external/jsoncpp_git/.*',
                        'external/highwayhash/.*',
                        'external/snappy/.*',
                        'external/nasm/.*',
                        'external/farmhash.*',
                        ]):
                    continue
                elif any(re.match(r, t['src'][0]) for r in [
                    '.*tensorflow/core/platform/s3/.*',
                        ]):
                    continue
            if 'CMD' == t['type']:
                if 'external/jpeg' in t['cmd']: continue
                if 'external/snappy' in t['cmd']: continue
                if 'external/com_google_protobuf' in t['cmd']: continue
                if 'external/nasm' in t['cmd']: continue
            G.append(t)
        for t in G:
            if t['type'] == 'CXX':
                if len(t['src']) == 0:
                    if DEBUG: print(t)
                else:
                    if DEBUG: print(t['src'])
            else:
                if DEBUG: print(t)
        return G
    @staticmethod
    def dedupGraph(depgraph: str):
        G = []
        for t in depgraph:
            if t['type'] == 'CXX':
                dup = [i for (i,x) in enumerate(G)
                        if (x['type'] == 'CXX') and (x['src'] == t['src']) and (x['obj'] == t['obj'])]
                if not dup:
                    G.append(t)
                else:
                    print('merging', t)
                    G[dup[0]]['flags'].extend(t['flags'])
            elif t['type'] == 'PROTOC':
                dup = [(i,x) for (i,x) in enumerate(G)
                        if (x['type'] == 'PROTOC') and (x['proto'] == t['proto'])]
                if not dup:
                    G.append(t)
                else:
                    #print('merging', t)
                    #G[dup[0][0]]['flags'].extend(t['flags'])
                    pass
            else:
                G.append(t)
        return G
    @staticmethod
    def generateNinja(depgraph: str, dest: str):
        '''
        Generate the NINJA file from the given depgraph
        '''
        dedupdir = set()
        F = Writer(open(dest, 'wt'))
        F.rule('PROTOC', 'protoc -I. $in $flags')
        F.rule('CXX', 'ccache g++ -I. -Iexternal -Iexternal/eigen3 -Iexternal/com_google_absl -O2 -fPIC $flags -c -o $out $in')
        F.rule('CXXEXEC', 'ccache g++ -I. -O2 -fPIE -pie $flags -o $out $in')
        F.rule('CXXSO', 'ccache g++ -fPIC $flags -o $out $in')
        F.rule('MKDIR', 'mkdir -p $out')
        F.rule('CP', 'cp -v $in $out')
        F.rule('PROTO_TEXT', './tensorflow/tools/proto_text/gen_proto_text_functions.elf $in')
        # protos_all_cc target
        protos = list(set(x['proto'][0] for x in depgraph if x['type']=='PROTOC'))
        F.build('protos_all_cc', 'phony', [re.sub('\.proto$', '.pb.cc', x) for x in protos])
        # gen_proto_text_function
        F.build('gen_proto_text_functions', 'phony', 'tensorflow/tools/proto_text/gen_proto_text_functions.elf')
        # inputs{1,2}_proto_text
        F.build('inputs1_proto_text', 'PROTO_TEXT', inputs1_proto_text,
                implicit='gen_proto_text_functions')
        F.build('inputs2_proto_text', 'PROTO_TEXT', inputs2_proto_text,
                implicit='gen_proto_text_functions')
        F.build('proto_text_all_cc', 'phony', ['inputs1_proto_text', 'inputs2_proto_text'])
        # small targets
        for t in depgraph:
            if t['type'] == 'CXX':
                # src obj flags
                src, obj, flags = t['src'], t['obj'], t['flags']
                flags = ' '.join(flags)
                assert(len(src) <= 1)
                assert(len(obj) == 1)
                src = '' if len(src)<1 else src[0]
                obj = obj[0]
                if re.match('.*\.c$', src) and obj.endswith('.o'):
                    F.build(obj, 'CXX', src, variables={'flags': flags}, implicit=['protoc_all_cc'])
                elif re.match('.*\.cc$', src) and obj.endswith('.o'):
                    if re.match('.*\.pb\.cc$', src):
                        F.build(obj, 'CXX', src, variables={'flags': flags}, implicit=['protos_all_cc', src])
                    elif re.match('.*\.pb_text\.cc', src):
                        F.build(src, 'phony', 'proto_text_all_cc', implicit=['protos_all_cc'])
                        F.build(obj, 'CXX', src, variables={'flags': flags}, implicit=['protos_all_cc'])
                    else:
                        F.build(obj, 'CXX', src, variables={'flags': flags}, implicit=['protos_all_cc'])
                elif re.match('.*\.cpp$', src) and obj.endswith('.o'):
                    F.build(obj, 'CXX', src, variables={'flags': flags}, implicit=['protos_all_cc'])
                elif re.match('.*gen_proto_text_functions.*', obj):
                    F.build(obj+'.elf', 'CXXEXEC', '', variables={'flags': flags},
                            implicit=[*objs_gen_proto_text_functions, 'protos_all_cc'])
                elif re.match('.*libtensorflow_framework.*', obj):
                    F.build(obj, 'CXXSO', '', variables={'flags': flags},
                            implicit=[*objs_libtensorflow_framework, 'protos_all_cc'])
                else:
                    print('???????', t)
            elif t['type'] == 'PROTOC':
                # proto flags
                assert(len(t['proto']) == 1)
                proto, flags = t['proto'][0], ' '.join(t['flags'])
                flags = re.sub('(.*)(--cpp_out=).*', '\\1\\2.', flags)
                F.build([re.sub('\.proto$', '.pb.cc', proto),
                    re.sub('\.proto$', '.pb.h', proto)],
                    'PROTOC', proto, variables={'flags': flags},
                    implicit=os.path.dirname(proto))
            elif t['type'] == 'CMD':
                if 'bazel-out/host/bin/tensorflow/tools/git/gen_git_source' in t['cmd']:
                    F.build('tensorflow/core/util/version_info.cc', 'CP',
                            'debian/patches/version_info.cc')
                else:
                    print('MISSING', FakeBazel.dirMangle(t['cmd']))
            else:
                print('MISSING', t)
        F.close()
    def __init__(self, path: str, dest: str = 'build.ninja'):
        print(f'* Parsing {path} ...')
        sys.stdout.flush()
        cmdlines = self.parseBuildlog(path)
        depgraph = self.understandCmdlines(cmdlines)
        print(f'  -> {len(cmdlines)} command lines -> {len(depgraph)} targets')
        sys.stdout.flush()
        depgraph = self.rinseGraph(depgraph)
        print(f'  -> {len(depgraph)} rinsed targets')
        depgraph = self.dedupGraph(depgraph)
        print(f'  -> {len(depgraph)} deduped targets')
        self.generateNinja(depgraph, dest)
        print(f'  -> Generated Ninja file {dest}')
        json.dump(depgraph, open('depgraph_debug.json', 'wt'), indent=4)


if os.path.exists('buildlogs'):
    fakeb = FakeBazel('buildlogs/libtensorflow_framework.so.log')
else:
    fakeb = FakeBazel('debian/buildlogs/libtensorflow_framework.so.log')

