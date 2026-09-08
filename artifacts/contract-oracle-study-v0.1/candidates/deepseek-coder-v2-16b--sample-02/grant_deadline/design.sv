module grant_deadline(
    input  logic clk,
    input  logic rst_n,
    input  logic request,
    output logic grant
);

    // Internal state variables
    enum logic {IDLE, WAITING} state, next_state;
    logic request_d1, request_d2; // Delayed versions of the request signal

    // State transition logic
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end

    // Next state logic based on current state and inputs
    always_comb begin
        case (state)
            IDLE: 
                if (request && !request_d1)
                    next_state = WAITING;
                else
                    next_state = IDLE;
            WAITING:
                if (!request_d2)
                    next_state = IDLE;
                else
                    next_state = WAITING;
        endcase
    end

    // Delays for the request signal to detect rising edges
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            request_d1 <= 0;
            request_d2 <= 0;
        end else begin
            request_d1 <= request;
            request_d2 <= request_d1;
        end
    end

    // Grant signal logic
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            grant <= 0;
        else if (state == WAITING && !request_d2)
            grant <= 1;
        else
            grant <= 0;
    end

endmodule
