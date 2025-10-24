#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(native, m, py::mod_gil_not_used()) {
  m.doc() = "高性能Webhook核心模块";

  m.def("fast_parse", &fast_parse, "高性能数据解析");
}
