module completion_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic event_done,
    output logic completed
);
    logic [1:0] state;
    parameter IDLE = 2'b00, DETECTED = 2'b01, PULSED = 2'b10;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            completed <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    if (event_done) begin
                        state <= DETECTED;
                    end else begin
                        state <= IDLE;
                    end
                    completed <= 1'b0;
                end
                DETECTED: begin
                    state <= PULSED;
                    completed <= 1'b1;
                end
                PULSED: begin
                    if (event_done) begin
                        state <= DETECTED;
                    end else begin
                        state <= IDLE;
                    end
                    completed <= 1'b0;
                end
            endcase
        end
    end
endmodule
