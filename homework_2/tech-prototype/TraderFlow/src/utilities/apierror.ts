class ApiError extends Error {
  code: number;
  title: string;
  constructor(code: number, message: string, title: string) {
    super(message);
    this.code = code;
    this.title = title;
  }
}

export default ApiError;
