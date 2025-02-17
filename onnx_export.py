import torch
from onnxexport.model_onnx import SynthesizerTrn
import utils

def main(NetExport):
    if not NetExport:
        return
    device = torch.device("cpu")
    path = "SoVits4.0"
    hps = utils.get_hparams_from_file(f"checkpoints/{path}/config.json")
    SVCVITS = SynthesizerTrn(
        hps.data.filter_length // 2 + 1,
        hps.train.segment_size // hps.data.hop_length,
        **hps.model)
    _ = utils.load_checkpoint(f"checkpoints/{path}/model.pth", SVCVITS, None)
    _ = SVCVITS.eval().to(device)
    for i in SVCVITS.parameters():
        i.requires_grad = False

    test_hidden_unit = torch.rand(1, 10, 256)
    test_pitch = torch.rand(1, 10)
    test_mel2ph = torch.LongTensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]).unsqueeze(0)
    test_uv = torch.ones(1, 10, dtype=torch.float32)
    test_noise = torch.randn(1, 192, 10)
    test_sid = torch.LongTensor([0])
    input_names = ["c", "f0", "mel2ph", "uv", "noise", "sid"]
    output_names = ["audio", ]

    torch.onnx.export(SVCVITS,
                      (
                          test_hidden_unit.to(device),
                          test_pitch.to(device),
                          test_mel2ph.to(device),
                          test_uv.to(device),
                          test_noise.to(device),
                          test_sid.to(device)
                      ),
                      f"checkpoints/{path}/model.onnx",
                      dynamic_axes={
                          "c": [0, 1],
                          "f0": [1],
                          "mel2ph": [1],
                          "uv": [1],
                          "noise": [2],
                      },
                      do_constant_folding=False,
                      opset_version=16,
                      verbose=False,
                      input_names=input_names,
                      output_names=output_names)


if __name__ == '__main__':
    main(True)
