export type Segment={exercise:string;start_seconds:number;end_seconds:number;duration_seconds:number;repetitions:number|null;repetitions_per_minute:number|null;intensity:string|null;met_value:number|null;calories_estimated:number;calories_low:number;calories_high:number;confidence:string;warnings:string[]};
export type AnalysisResult={duration_seconds:number;total_calories_estimated:number;total_calories_low:number;total_calories_high:number;overall_confidence:string;valid_pose_frame_ratio:number;frames_analyzed:number;segments:Segment[];exercise_totals:Record<string,{sets:number;repetitions:number;duration_seconds:number;calories_estimated:number}>;unknown_duration_seconds:number;warnings:string[]};

export function segmentPercent(segment:Segment,total:number){return total>0?Math.max(0,(segment.duration_seconds/total)*100):0}
export function activeSegmentIndex(segments:Segment[],time:number){return segments.findIndex(segment=>time>=segment.start_seconds&&time<segment.end_seconds)}
