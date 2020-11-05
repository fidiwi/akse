import pytest
import os
import AKsE
import filecmp


AKsE.startProgram()
file_output = "output.cpp"
file_expected = "output_expected.cpp"

comp = filecmp.cmp(file_expected, file_output, shallow=False)

assert comp
