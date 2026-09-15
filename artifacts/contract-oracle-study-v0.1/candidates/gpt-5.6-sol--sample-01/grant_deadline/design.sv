module grant_deadline(
    input  logic clk,
    input  logic rst_n,
    input  logic request,
    output logic grant
);

    logic pending;
    logic waited_one_cycle;

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            pending          <= 1'b0;
            waited_one_cycle <= 1'b0;
            grant            <= 1'b0;
        end else begin
            grant <= 1'b0;

            if (!pending) begin
                waited_one_cycle <= 1'b0;
                if (request) begin
                    pending <= 1'b1;
                end
            end else if (!waited_one_cycle) begin
                waited_one_cycle <= 1'b1;
            end else begin
                grant            <= 1'b1;
                pending          <= 1'b0;
                waited_one_cycle <= 1'b0;
            end
        end
    end

endmodule
