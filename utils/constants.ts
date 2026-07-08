export const ADMIN_REVIEW_PAGE_SIZE = 10;

export const REVIEW_STATUS_LABELS = {
  pending: "Pending",
  approved: "Approved",
  rejected: "Rejected",
} as const;

export const TESTIMONIAL_SOURCE_LABELS = {
  review: "Review",
  manual: "Manual",
} as const;

export const FRIENDLY_ERROR_MESSAGES: Record<number, string> = {
  400: "The request could not be processed. Check the entered values and try again.",
  401: "Your admin session has expired. Please sign in again.",
  403: "You do not have permission to perform this action.",
  404: "The requested item was not found.",
  409: "This action conflicts with the current item state. Refresh and try again.",
  422: "Some fields are invalid. Review the form and try again.",
  500: "The server encountered an error. Please try again shortly.",
};

export const cn = (...classes: Array<string | false | null | undefined>) => classes.filter(Boolean).join(" ");
