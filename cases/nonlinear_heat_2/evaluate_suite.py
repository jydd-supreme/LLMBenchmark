#!/usr/bin/env python3
"""Score equation diagnosis and future-temperature predictions."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def metrics(pred, ref):
    errors=[p-r for p,r in zip(pred,ref)]
    return {"mae":sum(abs(e) for e in errors)/len(errors),
            "rmse":math.sqrt(sum(e*e for e in errors)/len(errors)),
            "max_abs":max(abs(e) for e in errors),
            "relative_l2":math.sqrt(sum(e*e for e in errors)/sum(r*r for r in ref))}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("prediction_root",type=Path,
                        help="Directory containing nonlinear_heat_N/answer.json or adapter output")
    parser.add_argument("--model-alias",type=str,
                        help="Read adapter output from nonlinear_heat_2_N/MODEL_ALIAS/answer.json")
    parser.add_argument("--suite-root",type=Path,default=Path(__file__).resolve().parent)
    args=parser.parse_args()
    rows=[]
    all_pred=[]; all_ref=[]
    for number in range(1,31):
        case=args.suite_root/f"nonlinear_heat_{number}"
        reference=json.loads((case/"reference_answer.json").read_text())
        if args.model_alias:
            prediction_path=args.prediction_root/f"nonlinear_heat_2_{number}"/args.model_alias/"answer.json"
        else:
            prediction_path=args.prediction_root/f"nonlinear_heat_{number}"/"answer.json"
        if not prediction_path.exists():
            rows.append({"case_id":reference["case_id"],"missing":True}); continue
        try:
            prediction=json.loads(prediction_path.read_text())
            expected=reference["equation_assessment"]
            observed=prediction["equation_assessment"]
            if not isinstance(observed.get("consistent"),bool):
                raise ValueError("equation_assessment.consistent must be boolean")
            consistency_ok=(observed["consistent"] is expected["consistent"])
            type_ok=(observed["error_type"]==expected["error_type"])
            if prediction.get("points")!=reference["points"]:
                raise ValueError("probe coordinates or order mismatch")
            ref_rows=reference["temperature_by_time"]
            pred_rows=prediction["temperature_by_time"]
            if prediction["case_id"]!=reference["case_id"] or len(pred_rows)!=len(ref_rows):
                raise ValueError("case_id or time-row mismatch")
            pvals=[]; rvals=[]
            for p,r in zip(pred_rows,ref_rows):
                if float(p["time"])!=float(r["time"]) or len(p["values"])!=len(r["values"]):
                    raise ValueError("time or value-count mismatch")
                pvals.extend(float(v) for v in p["values"])
                rvals.extend(float(v) for v in r["values"])
            if not all(math.isfinite(v) for v in pvals): raise ValueError("non-finite temperature")
            result={"case_id":reference["case_id"],"missing":False,
                    "expected_consistent":expected["consistent"],
                    "expected_error_type":expected["error_type"],
                    "consistency_correct":consistency_ok,"error_type_correct":type_ok,
                    "temperature":metrics(pvals,rvals)}
            all_pred.extend(pvals); all_ref.extend(rvals); rows.append(result)
        except Exception as exc:
            rows.append({"case_id":reference["case_id"],"missing":False,"invalid":str(exc)})
    valid=[r for r in rows if not r.get("missing") and not r.get("invalid")]
    consistent=[r for r in valid if r["expected_consistent"]]
    inconsistent=[r for r in valid if not r["expected_consistent"]]
    true_rate=(sum(r["consistency_correct"] for r in consistent)/len(consistent)
               if consistent else None)
    false_rate=(sum(r["consistency_correct"] for r in inconsistent)/len(inconsistent)
                if inconsistent else None)
    labels=sorted({r["expected_error_type"] for r in valid})
    per_type_recall={label:sum(r["error_type_correct"] for r in valid
                               if r["expected_error_type"]==label)
                     /sum(r["expected_error_type"]==label for r in valid)
                     for label in labels}
    summary={"cases_expected":30,"cases_valid":len(valid),
             "equation_consistency_accuracy":sum(r["consistency_correct"] for r in valid)/len(valid) if valid else None,
             "equation_consistency_balanced_accuracy":(
                 (true_rate+false_rate)/2 if true_rate is not None and false_rate is not None else None),
             "error_type_accuracy":sum(r["error_type_correct"] for r in valid)/len(valid) if valid else None,
             "error_type_macro_recall":(
                 sum(per_type_recall.values())/len(per_type_recall) if per_type_recall else None),
             "error_type_recall_by_class":per_type_recall,
             "temperature":metrics(all_pred,all_ref) if all_pred else {},"cases":rows}
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
