import {describe,expect,it} from "vitest";
import {activeSegmentIndex,segmentPercent,type Segment} from "../lib/results";
const segment=(start:number,end:number):Segment=>({exercise:"squat",start_seconds:start,end_seconds:end,duration_seconds:end-start,repetitions:1,repetitions_per_minute:1,intensity:"light",met_value:3.5,calories_estimated:1,calories_low:.8,calories_high:1.2,confidence:"high",warnings:[]});
describe("result timeline",()=>{it("finds the active segment",()=>{expect(activeSegmentIndex([segment(0,3),segment(3,6)],4)).toBe(1)});it("calculates proportional widths",()=>{expect(segmentPercent(segment(0,2),10)).toBe(20)})});
