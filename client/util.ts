import { HttpParams } from '@angular/common/http';

export function getStepTitle(stepId: string): string {
  return stepId.replace('message_', '').replace(/_/g, ' ');
}

export function getQueryParams<T>(queryObject: T): HttpParams {
  let params = new HttpParams();
  const q = <[ keyof T ]>Object.keys(queryObject);
  for (const key of q) {
    if (queryObject[ key ] !== null && queryObject[ key ] !== undefined) {
      params = params.set(key, encodeURIComponent(queryObject[ key ].toString()));
    }
  }
  return params;
}
