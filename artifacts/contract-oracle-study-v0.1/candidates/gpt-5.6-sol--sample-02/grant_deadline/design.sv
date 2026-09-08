module grant_deadline(
    input  logic clk,
    input  logic rst_n,
    input  logic request,
    output logic grant
);

    typedef enum logic [1:0] {
        IDLE,
        WAIT_FIRST,
        WAIT_SECOND
    } state_t;

    state_t state;

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            state <= IDLE;
            grant <= 1'b0;
        end else begin
            grant <= 1'b0;

            case (state)
                IDLE: begin
                    if (request)
                        state <= WAIT_FIRST;
                end

                WAIT_FIRST: begin
                    state <= WAIT_SECOND;
                end

                WAIT_SECOND: begin
                    grant <= 1'b1;
                    state <= IDLE;
                end

                default: begin
                    state <= IDLE;
                end
            endcase
        end
    end

endmodule
